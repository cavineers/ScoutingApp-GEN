let objectLayout = [null, null];
const objectOrder = [null, "game-piece"];

const UNSELECTED_COLOR = "#777";
const PIECE_COLOR = "#FF4E4E";
const PIECE_BORDER_COLOR = "#FF4E4E";

window.addEventListener("load", () => {
    let buttons = document.getElementsByClassName("piece-button");
    for (let i = 0; i<buttons.length; i++) {
        buttons[i].addEventListener("click", (ev) => {
            if (ev.button!=0) return;
            objectLayout[i] = objectOrder[(objectOrder.indexOf(objectLayout[i])+1)%objectOrder.length];
            switch(objectLayout[i]) {
                case "game-piece":
                    buttons[i].style.background = PIECE_COLOR;
                    buttons[i].style.borderColor = PIECE_BORDER_COLOR;
                    break;
                default:
                    buttons[i].style.background = UNSELECTED_COLOR;
                    buttons[i].style.borderColor = UNSELECTED_COLOR;
                    break;
            }
        });
    }
});