import("./prematch.js");
import("./scout.js");
import("./result.js");

window.addEventListener("load", async () => {

    if(document.getElementById("submitForm") != null) {
        var namesResponse = await fetch("/names");
        /*An array containing all the country names in the world:*/
        var names = await namesResponse.json();
        /*initiate the autocomplete function on the "myInput" element, and pass along the countries array as possible autocomplete values:*/
        autocomplete(document.getElementById("name"), names);
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

    if(document.getElementById("nextButton2") != null || document.getElementById("endAuto") != null) {
        switchAuto();
        const endAutoButton = document.getElementById("endAuto");
        endAutoButton.addEventListener("click", (ev) => {
            if(ev.button != 0)
                return;
            const chargeOff = document.getElementById("chargeOffAuto");
            const chargeDocked = document.getElementById("chargeDockedAuto");
            const chargeEngaged = document.getElementById("chargeEngagedAuto");
            const state = chargeEngaged.checked ? chargeEngaged.value :
                      chargeDocked.checked ? chargeDocked.value :
                      chargeOff.value;
            localStorage.setItem(AUTO_CHARGE_STORAGE, JSON.stringify(state))
            localStorage.setItem(END_AUTO_STORAGE, JSON.stringify(getUTCNow()));

            //end auto button
            switchTele();
        });

        //next button
        const nextButton2 = document.getElementById("nextButton2");
        nextButton2.addEventListener("click", (ev) => {
            if (ev.button != 0)
                return;
            const chargeOff = document.getElementById("chargeOff");
            const chargeDocked = document.getElementById("chargeDocked");
            const chargeEngaged = document.getElementById("chargeEngaged");
            const state = chargeEngaged.checked ? chargeEngaged.value :
                      chargeDocked.checked ? chargeDocked.value :
                      chargeOff.value;
            //save
            localStorage.setItem(CHARGE_STORAGE, JSON.stringify(state));
            //redundant save
            localStorage.setItem(SCORE_GRID_STORAGE, JSON.stringify(scoreNodes));
            localStorage.setItem(ACTION1, JSON.stringify(action1));
            localStorage.setItem(ACTION2, JSON.stringify(action2));
            localStorage.setItem(ACTION3, JSON.stringify(action3));
            localStorage.setItem(ACTION4, JSON.stringify(action4));

            //go to result.html
            window.location.href = "/result.html";
        });
    }

    if(document.getElementById("finishButton") != null) {
        const finishButton = document.getElementById("finishButton");
        finishButton.addEventListener("click", async (ev) => {
            if (ev.button != 0)
                return;
            //TODO add any more comments, or change to set string to localStorage instead of array
            localStorage.setItem("comments", JSON.stringify([document.getElementById("commentarea1").value]));
            const data = new FormData();
            data.set("data", JSON.stringify(collectData()));
            await fetch("/upload", {
                method:"POST",
                body: data
            });

            //go back to home.html
            window.location.href = "/home.html";
        });
    }
});