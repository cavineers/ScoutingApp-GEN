let objectLayout = [null, null, null];
const objectOrder = ["game-piece", null];

const UNSELECTED_COLOR = "#777";
const PIECE_COLOR = "#ff0";
const PIECE_BORDER_COLOR = "#cc0";

window.addEventListener("load", () => {
    let buttons = document.getElementsByClassName("game-piece");
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