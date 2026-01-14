const network_key = "`{NETWORK_KEY}`"
window.dispatchEvent(new CustomEvent("NetworkDisconnect", {"detail" : {'net_key' : network_key}}));