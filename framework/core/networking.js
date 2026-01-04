import {Peer} from "https://esm.sh/peerjs@1.5.5?bundle-deps";

const global_id = "sfafsafsaffsfass";
//peerjs --port 5000 --key peerjs --path /
//This is for local testing when peerjs is down
//my savior https://lightrun.com/answers/peers-peerjs-server-receives-candidate-message-from-client-but-never-responds-to-it
class NetworkClient {
    static createPeer(id, callback=()=>{}){
        let peer = new Peer(id, {
            debug: 3,
            /*
            port: 5000,
            path: '/',
            host: 'localhost'
            */

        });
        peer.on('open', (ID)=>{
            console.log('My peer ID is: ' + ID);
            callback();
        });
        return peer;
    }
    
    constructor(is_host, the_id, message_handler = (data) => {console.log(`Received "${data}"`)}, 
    error_handler = (error) => {console.log(error)}, on_close = () => {}, on_dc = () => {}, on_connection = () => {}) {
        this.is_host = is_host;
        this.connection_id = the_id;
        this.is_connected = false;
        if (is_host) {
            this.peer = NetworkClient.createPeer(the_id, () => {
                this.peer.on('connection', (connection)=>{
                    this.connection = connection;
                    this.connection.on('data', message_handler);
                    this.peer.on('error', error_handler);
                    this.peer.on('close', on_close);
                    this.peer.on('disconnected', on_dc);
                    this.is_connected = true;
                    on_connection();
                });
            });
        } else {
            this.peer = NetworkClient.createPeer('', ()=>{
		        this.connection = this.peer.connect(the_id);
		        this.connection.on('open', ()=>{
                    this.connection.on('data', message_handler);
                    this.peer.on('error', error_handler);
                    this.peer.on('close', on_close);
                    this.peer.on('disconnected', on_dc);
                    this.is_connected = true;
                    on_connection();
		        });
	        });
        }
    }
    sendMessage(data) {
        if (this.connection !== undefined && this.is_connected) {
            this.connection.send(data);
        } else {
            console.log(`Attempted to send ${data}, but the connection was not yet established!`)
        }
    }
}
export {Peer, NetworkClient, global_id};