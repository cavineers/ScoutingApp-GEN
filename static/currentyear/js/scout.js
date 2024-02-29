/** @type {Array.<ScorePiece>} */
let scorePieces = [];
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

const PIECE = "piece"

const UNSELECTED_COLOR = "#777";
const PIECE_COLOR = "#ff0";
const PIECE_BORDER_COLOR = "#cc0";

document.addEventListener("DOMContentLoaded", function() {var undoContainer = document.getElementById("undoContainer");});

var undoValues = [];

var displayTime = "00:00:00";
var seconds = 0;
var minutes = 0;
var hours = 0;

function updateTime() {
  seconds++;
  if (seconds==60) {
      seconds = 0;
      minutes++;
  }
  if (minutes==60) {
      minutes = 0;
      hours++;
  }
  if (seconds < 10) {displaySeconds = "0" + seconds;} else {displaySeconds = seconds;}
  if (minutes < 10) {displayMinutes = "0" + minutes;} else {displaySeconds = minutes;}
  if (hours < 10) {displayHours = "0" + hours;} else {displaySeconds = hours;}
  displayTime = displayHours + ":" + displayMinutes + ":" + displaySeconds;
}

setInterval(updateTime, 1000);

function getUTCNow() {
    let d = new Date();
    return d.getTime() + d.getTimezoneOffset()*60000; //60000 ms in 1 minute 
}

function getUTCNow() {
    let d = new Date();
    return d.getTime() + d.getTimezoneOffset()*60000; //60000 ms in 1 minute
}

class ScorePiece {

    /**
     * 
     * @param {Element} element Element to check the classList of.
     * @returns {string|null} The node type, or null if could not be determined.
     */

    static pieceTypeFromClass(element) {
        return element.classList.contains("piece");
    }

    /**
     * 
     * @param {Element} element 
     * @param {string} type Type of score piece.
     * @param {string|null} piece Game piece that is in the node.
     * @param {object} history
     */

    constructor(element, type, piece, history) {
        this.element = element;
        this.type = !type ? ScorePiece.pieceTypeFromClass(element) : type;
        this.piece = Object.values(PIECE).includes(piece) ? piece : null;
        this.history = history?history:{};
    }

    /**
     * Set the Score Node's Game Piece
     * @param {string|null} piece
     */
    setPiece(piece) {
        this.piece = piece;
        this.history[getUTCNow()] = Object.values(NOTE).includes(piece) ? piece : null;
        if (piece==PIECE) {
            this.element.style.background = PIECE_COLOR;
            this.element.style.borderColor = PIECE_BORDER_COLOR;
        } else {
            this.element.style.background = UNSELECTED_COLOR;
            this.element.style.borderColor = UNSELECTED_COLOR;
        }
    }
}


window.addEventListener("load", () => {
    const selections = document.querySelectorAll(".piece-button");
    selections.forEach((selection) => {
        let pieces = new ScorePiece(selection);
        scorePieces.push(pieces);
        setPieceClick(pieces)
    });

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

/**
 * @param {ScorePiece} scorePiece
 */
function setPieceClick(scorePiece) {
    scorePiece.element.addEventListener("click", (e) => {
                if (scorePiece.piece == null)
                    scorePiece.setPiece(PIECE);
                else
                    scorePiece.setPiece(null);
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