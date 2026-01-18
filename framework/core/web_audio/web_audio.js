let path = "`{AUDIO_PATH}`";
let active = `{PLAY_NOW}`;
let id = `{CHANNEL_ID}`;

let volume = `{VOLUME}`;
let target_loop_count = `{LOOP_COUNT}`;
let current_loop_count = 0;

let audio = new Audio(path);
audio.onended = when_audio_ends;
audio.volume = volume;
if (!path.includes('audio/NOTHING.ogg')) {
    if (active) {
        audio.play();
        console.log(`Started audio playback of ${path} on channel ${id}`);
    } else {
        console.log(`Loaded audio ${path} on channel ${id}`);
    }
} else {
    active = false
}

window.addEventListener('StartAudio', (event) => {
    //id, path, volume, target_loop_count, dont_play = false
    if (event.detail.id !== id) {return;}
    audio.pause();
    
    audio = new Audio(event.detail.path);
    audio.onended = when_audio_ends;
    audio.volume = event.detail.volume;
    volume = event.detail.volume;
    current_loop_count = 0;
    target_loop_count = event.detail.target_loop_count;
    
    if ((!event.detail.dont_play) || (event.detail.dont_play === undefined)) {
        audio.play();
        console.log(`Started audio playback of ${event.detail.path} on channel ${event.detail.id}`)
    } else {
        console.log(`Loaded audio ${event.detail.path} on channel ${event.detail.id}`)
    }
    path = event.detail.path;
    active = true;
})

const b = 'WebAudioChannel' + id.toString() + "_";
localStorage.setItem(b + "volume", audio.volume.toString());
localStorage.setItem(b + "busy", (active).toString());

window.addEventListener('StopAudio', (event) => {
    //id
    if (event.detail.id !== id) {return;}
    audio.pause();
    console.log(`Stopped audio playback of ${path} on channel ${event.detail.id}`);
    localStorage.setItem(base_key + "volume", "0");
    localStorage.setItem(base_key + "busy", "false");
    active = false;
})

window.addEventListener('UpdateVolume', (event) => {
    //id, volume
    if (event.detail.id !== id) {return;}
    audio.volume = event.detail.volume;
    volume = event.detail.volume
})

window.addEventListener('PauseAudio', (event) => {
    //id
    if (event.detail.id !== id) {return;}
    audio.pause();
})

window.addEventListener('ResumeAudio', (event) => {
    //id
    if (event.detail.id !== id || !(active)) {return;}
    if (audio.paused) {
        audio.play();
    }
})

window.addEventListener('UpdateAudioChannel', (event) => {
    //id
    if (event.detail.id !== id) {return;}
    const base_key = 'WebAudioChannel' + id.toString() + "_";
    localStorage.setItem(base_key + "volume", audio.volume.toString());
    localStorage.setItem(base_key + "busy", (active).toString());
})

function when_audio_ends(event) {
    if (event.target !== audio) {return;}
    if (target_loop_count < 0 || current_loop_count < target_loop_count) {
        current_loop_count += 1;
        audio.currentTime = 0;
        audio.play();
    } else {
        active = false;
        const base_key = 'WebAudioChannel' + id.toString() + "_";
        localStorage.setItem(base_key + "busy", (active).toString());
        console.log(`Ended audio playback of ${path} on channel ${id}`);
    }
}