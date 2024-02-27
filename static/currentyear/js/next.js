window.addEventListener("load", async () => {

    //Home Page
    if(document.getElementById("submitForm") != null) {
        //calls for list of names
        var namesResponse = await fetch("/names")
        //list of scouter names
        var names = await namesResponse.json();
        /*initiate the autocomplete function on the "myInput" element, and pass along the countries array as possible autocomplete values:*/
        document.getElementById(("name"), names);
        let submitForm = document.getElementById("submitForm");
        submitForm.addEventListener("submit", (ev) => {
            ev.preventDefault();
            const found = document.getElementsByClassName("input");
            let inputs = {};
            for(let input of found)
                inputs[input.name] = input.type == "number" ? Number(input.value) : input.value;
            //verify info
            if (!verifyInfo(inputs))
                return;
            //save info
            localStorage.setItem("preliminaryData", JSON.stringify(inputs));
            window.location.href = "/prematch.html";
        });
    }

    //Prematch Page
    if(document.getElementById("nextButton") != null) {
        const nextButton = document.getElementById("nextButton");
        nextButton.addEventListener("click", (ev) => {
            if (ev.button != 0)
                return;
            //startObject: startNone|startObject2|startObject1
            //roboPos: left|mid|right
            localStorage.setItem("objectLayout", JSON.stringify(objectLayout));
            for (let input of document.getElementsByTagName("input")) {
                if (input.type == "radio" && !input.checked) continue;
                localStorage.setItem(input.name, JSON.stringify(input.value));
            }

            //go to next page
            window.location.href = "/scout.html";
        });
    }

    //Scout Page (Auto and Teleop)
    if(document.getElementById("scoutNext") != null || document.getElementById("endAuto") != null) {
        //loads auto page
        switchAuto();

        //end auto button
        const endAutoButton = document.getElementById("endAuto");
        endAutoButton.addEventListener("click", (ev) => {
            if(ev.button != 0)
                return;
            //gets robot state data for auto
            const offState = document.getElementById("autoOffState");
            const state1 = document.getElementById("autoState1");
            const state2 = document.getElementById("autoState2");
            const state = state2.checked ? state2.value :
                      state1.checked ? state1.value :
                      offState.value;
            //saves auto button clicks and auto robot state
            localStorage.setItem(AUTO_STATE, JSON.stringify(state));
            localStorage.setItem(AUTO_ACTION_1, JSON.stringify(autoActions1));
            localStorage.setItem(AUTO_ACTION_2, JSON.stringify(autoActions2));
            localStorage.setItem(AUTO_ACTION_3, JSON.stringify(autoActions3));
            localStorage.setItem(AUTO_ACTION_4, JSON.stringify(autoActions4));
            localStorage.setItem(END_AUTO_STORAGE, JSON.stringify(getUTCNow()));

            //end auto button
            switchTele();
        });

        //Next button
        const nextButton2 = document.getElementById("scoutNext");
        nextButton2.addEventListener("click", (ev) => {
            if (ev.button != 0)
                return;
            //Gets robot state data for teleop
            const offState = document.getElementById("offState");
            const state1 = document.getElementById("state1");
            const state2 = document.getElementById("state2");
            const state = state2.checked ? state2.value :
                      state1.checked ? state1.value :
                      offState.value;
            //saves button clicks and robot state
            localStorage.setItem(TELE_STATE, JSON.stringify(state));
            localStorage.setItem(TELE_ACTION_1, JSON.stringify(teleActions1));
            localStorage.setItem(TELE_ACTION_2, JSON.stringify(teleActions2));
            localStorage.setItem(TELE_ACTION_3, JSON.stringify(teleActions3));
            localStorage.setItem(TELE_ACTION_4, JSON.stringify(teleActions4));

            //go to result.html
            window.location.href = "/result.html";
        });
    }

    //Results Page
    if(document.getElementById("finishButton") != null) {
        //submit button
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