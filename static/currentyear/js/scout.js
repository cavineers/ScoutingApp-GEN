/** @type {Array.<ScoreNode>} */
let scoreNodes = [];
/** @type {Array.<number>} */
let actions1 = []
/** @type {Array.<number>} */
let actions2 = [];
/** @type {Array.<number>} */
let actions3 = [];
/** @type {Array.<number>} */
let actions4 = [];


const SCORE_GRID_STORAGE = "scoreGrid";
const ACTION1 = "action1"; // actions 1
const ACTION2 = "action2"; // actions 2
const ACTION3 = "action3"; // actions 3
const ACTION4 = "action4"; // action 4
const CHARGE_STORAGE = "chargeState";
const AUTO_CHARGE_STORAGE = "autoChargeState";
const END_AUTO_STORAGE = "endAuto";
const AUTO_ACTION4 = "autoAction4"; // auto 4

const NodeType = {
    Object1: "object1",
    Object2: "object2",
    Both: "both"
};

const GamePiece = {
    Object1: "object1",
    Object2: "object2"
};

const UNSELECTED_COLOR = "#777";
const OBJECT1_COLOR = "#ff0";
const OBJECT1_BORDER_COLOR = "#cc0";
const OBJECT2_COLOR = "#b0f";
const OBJECT2_BORDER_COLOR = "#80c";

function getUTCNow() {
    let d = new Date();
    return d.getTime() + d.getTimezoneOffset()*60000; //60000 ms in 1 minute
}

class ScoreNode {

    /**
     * 
     * @param {Element} element Element to check the classList of.
     * @returns {string|null} The node type, or null if could not be determined.
     */

    static nodeTypeFromClass(element) {
        return element.classList.contains("node-object1") ? NodeType.Object1 : element.classList.contains("node-object2") ? NodeType.Object2 : element.classList.contains("node-both") ? NodeType.Both : null;
    }

    /**
     * 
     * @param {Element} element 
     * @param {string} type Type of score node.
     * @param {string|null} gamePiece Game piece that is in the node.
     * @param {object} history
     */

    constructor(element, type, gamePiece, history) {
        this.element = element;
        this.type = !type ? ScoreNode.nodeTypeFromClass(element) : type;
        this.gamePiece = Object.values(GamePiece).includes(gamePiece) ? gamePiece : null;
        this.history = history?history:{};
    }

    /**
     * Set the Score Node's Game Piece
     * @param {string|null} gamePiece
     */
    setGamePiece(gamePiece) {
        this.gamePiece = gamePiece;
        this.history[getUTCNow()] = Object.values(GamePiece).includes(gamePiece) ? gamePiece : null;
        if (gamePiece==GamePiece.Object1) {
            this.element.style.background = OBJECT1_COLOR;
            this.element.style.borderColor = OBJECT1_BORDER_COLOR;
        }
        else if (gamePiece==GamePiece.Object2) {
            this.element.style.background = OBJECT2_COLOR;
            this.element.style.borderColor = OBJECT2_BORDER_COLOR;
        }
        else {
            this.element.style.background = UNSELECTED_COLOR;
            this.element.style.borderColor = UNSELECTED_COLOR;
        }
        localStorage.setItem(SCORE_GRID_STORAGE, JSON.stringify(scoreNodes));
    }
}


window.addEventListener("load", () => {
    const selections = document.querySelectorAll(".node-object1, .node-object2, .node-both");
    selections.forEach((selection) => {
        let node = new ScoreNode(selection);
        scoreNodes.push(node);
        setNodeClick(node);
    });

    //track button press times
    const action1 = document.getElementById("action1");
    const action2 = document.getElementById("action2");
    const action3 = document.getElementById("action3");
    const action4 = document.getElementById("action4");
    const autoAction1 = document.getElementById("auto_action1");
    const autoAction2 = document.getElementById("auto_action2");
    const autoAction3 = document.getElementById("auto_action3");
    const autoAction4 = document.getElementById("auto_action4");
    if (!localStorage.getItem(AUTO_ACTION4))
        localStorage.setItem(AUTO_ACTION4, "null");

    setMarkTime(action1, ACTION1, actions1);
    setMarkTime(action2, ACTION2, actions2);
    setMarkTime(action3, ACTION3, actions3);
    setMarkTime(action4, ACTION4, actions4);
    setMarkTime(autoAction1, ACTION1, actions1);
    setMarkTime(autoAction2, ACTION2, actions2);
    setMarkTime(autoAction3, ACTION3, actions3);
    autoAction4.addEventListener("click", (ev)=>{
        if (ev.button!=0) return;
        localStorage.setItem(AUTO_ACTION4, getUTCNow());
    })
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

/**
 * @param {ScoreNode} scoreNode
 */
function setNodeClick(scoreNode) {
    scoreNode.element.addEventListener("click", (e) => {
        switch(scoreNode.type) {
            case NodeType.Object1:
                if (scoreNode.gamePiece == null)
                    scoreNode.setGamePiece(GamePiece.Object1);
                else
                    scoreNode.setGamePiece(null);
                break;
            case NodeType.Object2:
                if (scoreNode.gamePiece == null)
                    scoreNode.setGamePiece(GamePiece.Object2);
                else
                    scoreNode.setGamePiece(null);
                break;
            case NodeType.Both:
                //define popup menu, get menu element
                if (scoreNode.gamePiece == null) {
                    let menuContainer = addMenu(null, "50%", "fit-content");
                    let menu = menuContainer.children[1];
                    menu.style.alignItems = "center";

                    //define button
                    let object1Button = document.createElement("button");
                    //set button style
                    object1Button.classList.add("node-object1_button");
                    object1Button.style.background = OBJECT1_COLOR;
                    object1Button.style.borderColor = OBJECT1_BORDER_COLOR;
                    //set button click event
                    object1Button.addEventListener("click", (ev) => {
                        if (ev.button != 0)
                            return;
                        scoreNode.setGamePiece(GamePiece.Object1);
                        menuContainer.remove();
                    });

                    //define button
                    let object2Button = document.createElement("button")
                    //set button style
                    object2Button.classList.add("node-object2_button");
                    object2Button.style.background = OBJECT2_COLOR;
                    object2Button.style.borderColor = OBJECT2_BORDER_COLOR;
                    object2Button.addEventListener("click", (ev) => {
                        if (ev.button != 0)
                            return;
                        scoreNode.setGamePiece(GamePiece.Object2);
                        menuContainer.remove();
                    });

                    menu.appendChild(object1Button);
                    menu.appendChild(object2Button);
                }
                else
                    scoreNode.setGamePiece(null);
                break;
        }
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