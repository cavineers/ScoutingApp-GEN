window.addEventListener("load", async () => {

    // Home Page
    if(document.getElementById("submitForm") != null) {
        /*An array containing all the country names in the world:*/
        var namesResponse = await fetch("/names");
        var names = await namesResponse.json();
        (document.getElementById("name"), names);
        // add event listener to the submitForm
        let submitForm = document.getElementById("submitForm");
        submitForm.addEventListener("submit", (ev) => {
            // get references to various chain-related elements in the document 
            const red1 = document.getElementById("red1");
            const red2 = document.getElementById("red2");
            const red3 = document.getElementById("red3");
            const blu1 = document.getElementById("blu1");
            const blu2 = document.getElementById("blu2");
            const blu3 = document.getElementById("blu3");
            // determine the selected chain based on the checked state of radio buttons
            const robotState = red1.checked ? red1.value :
                        red2.checked ? red2.value :
                        red3.checked ? red3.value :
                        blu1.checked ? blu1.value :
                        blu2.checked ? blu2.value :
                        blu3.checked ? blu3.value :
            localStorage.setItem(ROBOT_STORAGE, JSON.stringify(robotState));  
            for (let input of document.getElementsByTagName("input")) {
                if (input.type == "radio" && !input.checked) continue;
                localStorage.setItem(input.name, JSON.stringify(input.value));
            }
            localStorage.setItem(robotOrder, JSON.stringify(robotOrder));
            ev.preventDefault();
            // collect form inputs into an object
            const found = document.getElementsByClassName("input");
            let inputs = {};
            for(let input of found)
                inputs[input.name] = input.type == "number" ? Number(input.value) : input.value; 
            // verify the collected information
            if (!verifyInfo(inputs))
                return;
            // save the collected information to local storage
            localStorage.setItem("preliminaryData", JSON.stringify(inputs));          
            // redirect to prematch
            window.location.href = "/prematch.html";
        });
    }

    // Prematch Page
    if(document.getElementById("nextButton") != null) {
        const nextButton = document.getElementById("nextButton");
        nextButton.addEventListener("click", (ev) => {
            if (ev.button != 0)
                return;
            // startObject: startNone|startObject2|startObject1
            // roboPos: left|mid|right
            localStorage.setItem("objectLayout", JSON.stringify(objectLayout));
            for (let input of document.getElementsByTagName("input")) {
                if (input.type == "radio" && !input.checked) continue;
                localStorage.setItem(input.name, JSON.stringify(input.value));
            }
            // go to next page
            window.location.href = "/scout.html";
        });
    }

    // Scout Page (Auto and Teleop)
    if(document.getElementById("scoutNext") != null || document.getElementById("endAuto") != null) {
        // calls the function to load the auto page
        switchAuto();
        // end auto button
        const endAutoButton = document.getElementById("endAuto");
        endAutoButton.addEventListener("click", (ev) => {
            if(ev.button != 0)
                return;
            // assigns html elements to tele states and finds the checked state
            const offState = document.getElementById("autoOffState");
            const state1 = document.getElementById("autoState1");
            const state2 = document.getElementById("autoState2");
            const state = state2.checked ? state2.value :
                      state1.checked ? state1.value :
                      offState.value;
            // converts list of buttons pressed and auto state as JSON data
            localStorage.setItem(AUTO_STATE, JSON.stringify(state));
            localStorage.setItem(AUTO_ACTION_1, JSON.stringify(autoActions1));
            localStorage.setItem(AUTO_ACTION_2, JSON.stringify(autoActions2));
            localStorage.setItem(AUTO_ACTION_3, JSON.stringify(autoActions3));
            localStorage.setItem(AUTO_ACTION_4, JSON.stringify(autoActions4));
            localStorage.setItem(END_AUTO_STORAGE, JSON.stringify(getUTCNow()));
            // calls the function to end auto period and begin teleop
            switchTele();
        });

        // creates a listener for the next-page button
        const nextButton2 = document.getElementById("scoutNext");
        nextButton2.addEventListener("click", (ev) => {
            if (ev.button != 0)
                return;
            // assigns html elements to tele states and finds the checked state
            const offState = document.getElementById("offState");
            const state1 = document.getElementById("state1");
            const state2 = document.getElementById("state2");
            const state = state2.checked ? state2.value :
                      state1.checked ? state1.value :
                      offState.value;
            // converts list of buttons pressed and tele state to JSON data
            localStorage.setItem(TELE_STATE, JSON.stringify(state));
            localStorage.setItem(TELE_ACTION_1, JSON.stringify(teleActions1));
            localStorage.setItem(TELE_ACTION_2, JSON.stringify(teleActions2));
            localStorage.setItem(TELE_ACTION_3, JSON.stringify(teleActions3));
            localStorage.setItem(TELE_ACTION_4, JSON.stringify(teleActions4));
            // go to result.html
            window.location.href = "/result.html";
        });
    }

    // Results Page
    if(document.getElementById("finishButton") != null) {
        // creates a listener for the submit button
        const finishButton = document.getElementById("finishButton");
        finishButton.addEventListener("click", async (ev) => {
            if (ev.button != 0)
                return;
            // save comments to local storage
            localStorage.setItem("comments", JSON.stringify([document.getElementById("commentarea1").value]));
            setTimeout(() => finishButton.type = "submit", 100);
            // create FormData and send collected data to the server via POST request
            const data = new FormData();
            data.set("data", JSON.stringify(collectData()));
            await fetch("/upload", {
                method:"POST",
                body: data
            });
            // redirect back to home
            window.location.href = "/home.html";
        });
    }
});