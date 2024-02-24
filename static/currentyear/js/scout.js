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
const ACTION_1 = "action1"; // actions 1
const ACTION_2 = "action2"; // actions 2
const ACTION_3 = "action3"; // actions 3
const ACTION_4 = "action4"; // action 4
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
    const action1 = document.getElementById("action1");
    const action2 = document.getElementById("action2");
    const action3 = document.getElementById("action3");
    const action4 = document.getElementById("action4");
    const autoAction1 = document.getElementById("autoAction1");
    const autoAction2 = document.getElementById("autoAction2");
    const autoAction3 = document.getElementById("autoAction3");
    const autoAction4 = document.getElementById("autoAction4");

    //logs button clicks
    setMarkTime(action1, ACTION_1, teleActions1);
    setMarkTime(action2, ACTION_2, teleActions2);
    setMarkTime(action3, ACTION_3, teleActions3);
    setMarkTime(action4, ACTION_4, teleActions4);
    setMarkTime(autoAction1, ACTION_1, autoActions1);
    setMarkTime(autoAction2, ACTION_2, autoActions2);
    setMarkTime(autoAction3, ACTION_3, autoActions3);
    setMarkTime(autoAction4, ACTION_4, autoActions4);
});

function setMarkTime(element, storageKey, array) {
    element.addEventListener("click", (ev) => {
        if (ev.button != 0)
            return;

        array.push(getUTCNow());
        localStorage.setItem(storageKey, JSON.stringify(array));
    });
}

/**
 * 
 * @param {number} col The column that the score node is on (start at 0)
 * @param {number} row The row that the score node is on (start at 0)
 * @returns {number} The index in the list scoreNodes that the scoreNode in the specified column and row is at.
 */
function coordinatesToIndex(col, row) {
    return row*9+col;
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