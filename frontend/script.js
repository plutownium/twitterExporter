// const digitalOceanServerIP = "http://165.227.78.120"
const localIP = "http://127.0.0.1:5000"

function sendAPIKeys() {
    const consumerToken = document.getElementById("consumerToken").value
    const consumerSecret = document.getElementById("consumerSecret").value
    const accessToken = document.getElementById("accessToken").value
    const accessSecret = document.getElementById("accessSecret").value
    const twitterHandle = document.getElementById("twitterHandle").value
    console.log("HEY:", consumerToken, consumerSecret)

    // are access token and access secret even needed? might be able to take them out...
    const valid = validateKeys(consumerToken, consumerSecret, twitterHandle)

    if (valid) {
        console.log("WTF:", consumerToken, consumerSecret, twitterHandle)
        // send data to server
        // const URL = `${localIP}/consumerToken/${consumerToken}/consumerSecret/${consumerSecret}/accessToken/${accessToken}/accessSecret/${accessSecret}/username/${twitterHandle}`
        const URL = `${localIP}/consumerToken/${consumerToken}/consumerSecret/${consumerSecret}/username/${twitterHandle}`

        console.log("sending..." + URL)
        axios.post(URL).then(response => console.log(response)).catch(err => console.log(err))
        // TODO: find out what the response is when the flask server is running

    } else {
        // inform user s/he needs to fix something
        const warningEl = document.getElementById("warning")
        warningEl.innerHTML = "You need to fix one of your API keys. Make sure it is valid then click Send again"
    }
}

function updateMessage() {
    // TODO: message validation for the DM. find out what the rules are
}

function sendMessage() {
    // send the message to the flask server and begin sending the DMs.
    // BONUS: also show a "cancel" code the user can send to the server.

    // TODO: find out what the response is and do something if need be
    axios.get(localIP + "/stop").then(response => console.log(response)).catch(err => console.log(err))
}

function validateKeys(consumerToken, consumerSecret, twitterHandle) {
    // TODO: create validation
    return true
}