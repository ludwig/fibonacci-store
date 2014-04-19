package main

import (
    "fmt"
    "log"
    "time"
    "text/template"
    "net/http"
    "github.com/gorilla/websocket"
    "github.com/garyburd/redigo/redis"
)

// ----------------------------------------------------------------------------

// redis will send us messages through this channel
var notifyChannel = make(chan []byte)

func main() {

    // subscribe the the redis channel "tasks:all" and forward those messages to notifyChannel
    go listenToRedisChannel("tasks:all")

    // listen for websocket connections from user's browsers
    go startWebsocketServer()

    // sleep forever
    select{}
}

// ----------------------------------------------------------------------------

func listenToRedisChannel(redisChannel string) {
    log.Printf("Subscribing to redis channel %q\n", redisChannel)

    // Connect to redis
    c, err := redis.Dial("tcp", ":6379")
    if err != nil {
        log.Println("Could not connect to redis")
        panic(err)
    }
    defer c.Close()

    // Subscribe to redisChannel
    psc := redis.PubSubConn{c}
    psc.Subscribe(redisChannel)

    // Forward any received messages to notifyChannel
    for {
        switch v := psc.Receive().(type) {
        case redis.Message:
            log.Printf("redis channel %q received message %v\n", v.Channel, v.Data)
            notifyChannel <- v.Data
        case redis.Subscription:
            log.Printf("redis %q %s %d\n", v.Channel, v.Kind, v.Count)
        case error:
            panic(v)
        }
    }
}

func startWebsocketServer() {
    log.Println("Starting websocket server")
    log.Println("For now, also serving / requests at http://localhost:8080/")
    go hub.run()
    http.HandleFunc("/", serveHome)
    http.HandleFunc("/ws", serveWebsocket)
    err := http.ListenAndServe(":8080", nil)
    if err != nil {
        log.Fatal("http.ListenAndServe: ", err)
    }
}

// ----------------------------------------------------------------------------

var homeTempl = template.Must(template.ParseFiles("./templates/ws.html"))

func serveHome(w http.ResponseWriter, r *http.Request) {
    if r.URL.Path != "/" {
        http.Error(w, "Not found", 404)
        return
    }
    if r.Method != "GET" {
        http.Error(w, "Method not allowed", 405)
        return
    }
    w.Header().Set("Content-Type", "text/html; charset=utf-8")
    homeTempl.Execute(w, r.Host)
}

func serveWebsocket(w http.ResponseWriter, r *http.Request) {
    if r.Method != "GET" {
        http.Error(w, "Method not allowed", 405)
        return
    }

    /* XXX: don't forget to re-enable this!
    if r.Header.Get("Origin") != ("http://" + r.Host) {
        http.Error(w, "Origin not allowed", 403)
        return
    } */

    ws, err := websocket.Upgrade(w, r, nil, 1024, 1024)
    if _, ok := err.(websocket.HandshakeError); ok {
        http.Error(w, "Not a websocket handshake", 400)
        return
    } else if err != nil {
        log.Println(err)
        return
    }

    c := &connection{send: make(chan[]byte, 256), ws: ws}
    hub.register <- c
    go c.writePump()
    c.readPump()
}

func testReceive() {
    // let's test that we can receive messages from notifyChannel
    for {
        select {
        case msg := <-notifyChannel:
            s := string(msg[:])
            fmt.Printf("websocket-server received %q\n", s)
            // XXX: in here, determine which user should receive the notification,
            // retrieve the task result from redis, retrieve the opened websockets for
            // that user and notify all of them that the result is available
        }
    }
}


// ----------------------------------------------------------------------------

type connectionHub struct {
    // Registered connections
    connections map[*connection]bool

    // Register requests for a connection
    register chan *connection

    // Unregister requests for a connection
    unregister chan *connection
}

var hub = connectionHub{
    connections:    make(map[*connection]bool),
    register:       make(chan *connection),
    unregister:     make(chan *connection),
}

func (h *connectionHub) run() {
    log.Println("hub is running")
    for {
        select {
        case c:= <-h.register:
            h.connections[c] = true
        case c := <-h.unregister:
            delete(h.connections, c)
            close(c.send)
        case msg := <-notifyChannel:
            for c := range h.connections {
                select {
                case c.send <- msg:
                    log.Printf("Sent %q to %v\n", string(msg[:]), c)
                default:
                    delete(h.connections, c)
                    close(c.send)
                    go c.ws.Close()
                }
            }
        }
    }
}

// ----------------------------------------------------------------------------

const (
    // Time allowed to write a message to the peer.
    writeWait = 10 * time.Second

    // Time allowed to read the next pong message from the peer.
    pongWait = 60 * time.Second

    // Send pings to peer with this period. Must be less than pongWait.
    pongPeriod = (pongWait * 9) / 10

    // Maximum message size allowed form peer
    maxMessageSize = 512
)

type connection struct {
    // The websocket connection
    ws *websocket.Conn

    // Buffered channel of outbound messages
    send chan []byte
}

func (c *connection) readPump() {
    defer func() {
        hub.unregister <- c
        c.ws.Close()
    }()

    c.ws.SetReadLimit(maxMessageSize)
    c.ws.SetReadDeadline(time.Now().Add(pongWait))
    c.ws.SetPongHandler(func(string) error {
        c.ws.SetReadDeadline(time.Now().Add(pongWait));
        return nil
    })

    for {
        _, msg, err := c.ws.ReadMessage()
        if err != nil {
            break;
        }
        // we comment out the followingline because we'll be ignoring all messages from the client
        //hub.broadcast <- msg
        log.Printf("client sent message %v\n", msg)
    }
}

// write() writes a message with the given message type and payload
func (c *connection) write(msgType int, payload []byte) error {
    c.ws.SetWriteDeadline(time.Now().Add(writeWait))
    return c.ws.WriteMessage(msgType, payload)
}

// writePump() pumps messages to the websocket connection
func (c *connection) writePump() {
    ticker := time.NewTicker(pongPeriod)

    defer func() {
        ticker.Stop()
        c.ws.Close()
    }()

    for {
        select {
        case msg, ok := <-c.send:
            if !ok {
                c.write(websocket.CloseMessage, []byte{})
                return
            }
            if err := c.write(websocket.TextMessage, msg); err != nil {
                return
            }
        case <-ticker.C:
            if err := c.write(websocket.PingMessage, []byte{}); err != nil {
                return
            }
        }
    }
}

