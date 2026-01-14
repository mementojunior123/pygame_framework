const path = "`{AUDIO_PATH}`";
const play_now = `{PLAY_NOW}`;
let id = `{CHANNEL_ID}`;

let volume = `{VOLUME}`;
let target_loop_count = `{LOOP_COUNT}`;
let current_loop_count = 0;

let audio = new Audio(path);
audio.volume = volume;
if (play_now) {
    audio.play();
}

window.addEventListener('StartAudio', (event) => {
    if (event.detail.id !== id) {return;}
    audio.currentTime = 0;
    audio.play();
    audio.current_loop_count = 0;
    console.log(`Started audio playback of ${path}`);
})

window.addEventListener('StopAudio', (event) => {
    if (event.detail.id !== id) {return;}
    id = null;
    audio.pause();
    console.log(`Stopped audio playback of ${path}`);
})

window.addEventListener('UpdateVolume', (event) => {
    if (event.detail.id !== id) {return;}
    audio.volume = event.detail.volume;
    volume = event.detail.volume
})

window.addEventListener('PauseAudio', (event) => {
    if (event.detail.id !== id) {return;}
    audio.pause();
})

window.addEventListener('UpdateAudioChannel', (event) => {
    if (event.detail.id !== id) {return;}
    const base_key = 'WebAudioChannel' + id.toString() + "_";
    localStorage.setItem(base_key + "volume", audio.volume.toString());
    localStorage.setItem(base_key + "playing", (!audio.paused).toString())
})

window.addEventListener('SwitchAudio', (event) => {
    if (event.detail.id !== id) {return;}
    audio.pause();
    
    audio = new Audio(event.detail.new_path);
    audio.volume = event.detail.volume;
    volume = event.detail.volume;
    current_loop_count = 0;
    target_loop_count = event.detail.target_loop_count
    if (event.detail.play_now) {audio.play();}
})