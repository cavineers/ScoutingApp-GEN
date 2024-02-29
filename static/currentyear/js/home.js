let robotLayout = ["red", "red", "red", "blu", "blu", "blu"];
const robotOrder = ["red1", "red2", "red3", "blu1", "blu2", "blu3"];

const RED1 = "red1";
const RED2 = "red2";
const RED3 = "red3";

const BLU1 = "blu1";
const BLU2 = "blu2";
const BLU3 = "blu3";

const ROBOT_STORAGE = "robot";

const UNSELECTED_COLOR = "#9a9280";
const RED_COLOR = "#aa0000";
const RED_BORDER_COLOR = "#aa0000";
const BLUE_COLOR = "#476291";
const BLUE_BORDER_COLOR = "#476291";

window.addEventListener("load", () => {
    let robot = document.querySelectorAll(".red, .blu");
    for (let i = 0; i<robot.length; i++) {
        robot[i].addEventListener("click", (ev) => {
            if (ev.button!=0) return;
            robotLayout[i] = robotOrder[(robotOrder.indexOf(robotLayout[i])+1)%robotOrder.length];
            switch(robotLayout[i]) {
                case "red":
                    robot[i].style.background = RED_COLOR;
                    robot[i].style.borderColor = RED_BORDER_COLOR;
                    break;
                case "blu":
                    robot[i].style.background = BLUE_COLOR;
                    robot[i].style.borderColor = BLUE_BORDER_COLOR;
                    break;
                default:
                    robot[i].style.background = UNSELECTED_COLOR;
                    robot[i].style.borderColor = UNSELECTED_COLOR;
                    break;
            }
        });
    }
});

function verifyInfo(inputs) {
    console.log(inputs.match)
    if (inputs.match < 1) {
        outputError("Invalid match number.");
        return false;
    }
    else if (inputs.team < 1) {
        outputError("Invalid team number.")
        return false;
    }
    else if (!inputs.scouter.trim() || inputs.scouter=="placeholder") {
        outputError("Enter your name (The name of the person scouting).");
        return false;
    }
    //TODO fix this
    else if (inputs.robot !== undefined) {
        outputError("Select alliance robot.")
        return false;
    }
    return true;
  }

function outputError(message) {
  console.error(message);
  let errorOutput = document.getElementById("errorOutput");
  if (errorOutput==null) {
    const submitForm = document.getElementById("submitForm");
    if (submitForm==null) return; //nowhere to visibly output error to
    errorOutput = document.createElement("p");
    errorOutput.style.color = "#be0000";
    errorOutput.id = "errorOutput";
    submitForm.prepend(errorOutput);
  }
  errorOutput.innerHTML = message;
}
