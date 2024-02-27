/** @type {Array.<number>} */
let autoActions1 = []
/** @type {Array.<number>} */
let autoActions2 = [];
/** @type {Array.<number>} */
let autoActions3 = [];
/** @type {Array.<number>} */
let autoActions4 = [];
/** @type {Array.<number>} */
let teleActions1 = []
/** @type {Array.<number>} */
let teleActions2 = [];
/** @type {Array.<number>} */
let teleActions3 = [];
/** @type {Array.<number>} */
let teleActions4 = [];



const AUTO_ACTION_1 = "autoAction1"; //picks up note during auto
const AUTO_ACTION_2 = "autoAction2"; //picks up note during auto
const AUTO_ACTION_3 = "autoAction3"; //picks up note during auto
const AUTO_ACTION_4 = "autoAction4"; // auto 4
const TELE_ACTION_1 = "teleAction1"; // actions 1
const TELE_ACTION_2 = "teleAction2"; // actions 2
const TELE_ACTION_3 = "teleAction3"; // actions 3
const TELE_ACTION_4 = "teleAction4"; // action 4
const TELE_STATE = "teleState";
const AUTO_STATE = "autoState";
const END_AUTO_STORAGE = "endAuto";

const GamePiece = "gamePiece"

const UNSELECTED_COLOR = "#777";
const PIECE_COLOR = "#ff0";
const PIECE_BORDER_COLOR = "#cc0";

function getUTCNow() {
    let d = new Date();
    return d.getTime() + d.getTimezoneOffset()*60000; //60000 ms in 1 minute
}

class Pieces {

    /**
     * 
     * @param {Element} element Element to check the classList of.
     * @returns {string|null} The node type, or null if could not be determined.
     */

    static getPiece(element) {
        return element.classList.contains("game-piece") ? GamePiece : null;
    }

    /**
     * 
     * @param {Element} element 
     * @param {string|null} gamePiece Game piece that is in the node.
     * @param {object} history
     */

    constructor(element, gamePiece, history) {
        this.element = element;
        this.gamePiece = getPiece(GamePiece) ? gamePiece : null;
        this.history = history?history:{};
    }

    /**
     * Set the Score Node's Game Piece
     * @param {string|null} gamePiece
     */
    setGamePiece(gamePiece) {
        this.gamePiece = gamePiece;
        if (GamePiece != null) {
            this.element.style.background = OBJECT1_COLOR;
            this.element.style.borderColor = OBJECT1_BORDER_COLOR;
        }
        else {
            this.element.style.background = UNSELECTED_COLOR;
            this.element.style.borderColor = UNSELECTED_COLOR;
        }
    }
}


window.addEventListener("load", () => {

    //declares scout page buttons
    const teleAction1 = document.getElementById("teleAction1");
    const teleAction2 = document.getElementById("teleAction2");
    const teleAction3 = document.getElementById("teleAction3");
    const teleAction4 = document.getElementById("teleAction4");
    const autoAction1 = document.getElementById("autoAction1");
    const autoAction2 = document.getElementById("autoAction2");
    const autoAction3 = document.getElementById("autoAction3");
    const autoAction4 = document.getElementById("autoAction4");

    //logs button clicks
    setMarkTime(autoAction1, AUTO_ACTION_1, autoActions1);
    setMarkTime(autoAction2, AUTO_ACTION_2, autoActions2);
    setMarkTime(autoAction3, AUTO_ACTION_3, autoActions3);
    setMarkTime(autoAction4, AUTO_ACTION_4, autoActions4);
    setMarkTime(teleAction1, TELE_ACTION_1, teleActions1);
    setMarkTime(teleAction2, TELE_ACTION_2, teleActions2);
    setMarkTime(teleAction3, TELE_ACTION_3, teleActions3);
    setMarkTime(teleAction4, TELE_ACTION_4, teleActions4);
});

function setMarkTime(element, storageKey, array) {
    element.addEventListener("click", (ev) => {
        if (ev.button != 0)
            return;

        array.push(getUTCNow());
        localStorage.setItem(storageKey, JSON.stringify(array));

        var button = document.createElement("button");
       undoValues[undoValues.length] = 1
       button.classList.add("undo_button")
       button.textContent = displayTime + " - " + element.innerHTML;
       button.number = undoValues.length
       button.addEventListener("click", function() {
           if (undoValues[button.number] == 1) {
               button.style.textDecoration = "line-through";
               button.style.backgroundColor = "#505050";
               button.style.color = "#808080";
               undoValues[button.number] = 0
           } else {
               button.style.textDecoration = "none";
               button.style.backgroundColor = "#727272";
               button.style.color = "white";
               undoValues[button.number] = 1
           }
       });
       undoContainer.insertAdjacentElement('afterbegin', button)
    });
}

let autoState = true;

function switchTele() {
    for (let elm of document.getElementsByClassName("auto"))
        elm.hidden = true;
    for (let elm of document.getElementsByClassName("tele"))
        elm.hidden = false;
}

function switchAuto() {
    for (let elm of document.getElementsByClassName("auto"))
        elm.hidden = false;
    for (let elm of document.getElementsByClassName("tele"))
        elm.hidden = true;
}

function toggleAutoTele() {
    autoState = !autoState;
    if (autoState)
        switchAuto();
    else
        switchTele();

}