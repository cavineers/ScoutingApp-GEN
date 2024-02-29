function collectData() {
    // create an object to store collected data
    let contents = {};

    // identify the type of content as "match"
    contents["contentType"] = "match";

    // retrieve and store preliminary match data
    contents["robotState"] = JSON.parse(localStorage.getItem("robotState"));
    contents["preliminaryData"] = JSON.parse(localStorage.getItem("preliminaryData"));
    contents["formatted_upload_date"] = JSON.parse(localStorage.getItem("formatted_upload_date"));
    contents["start"] = JSON.parse(localStorage.getItem("start"));

    // retrieve and store pre-match data
    contents["roboPos"] = JSON.parse(localStorage.getItem("roboPos"));
    contents["startObject"] = JSON.parse(localStorage.getItem("startObject"));

    //get scout data
    contents["autoAction1"] = JSON.parse(localStorage.getItem("autoAction1"));
    contents["autoAction2"] = JSON.parse(localStorage.getItem("autoAction2"));
    contents["autoAction3"] = JSON.parse(localStorage.getItem("autoAction3"));
    contents["autoAction4"] = JSON.parse(localStorage.getItem("autoAction4"));
    contents["teleAction1"] = JSON.parse(localStorage.getItem("teleAction1"));
    contents["teleAction2"] = JSON.parse(localStorage.getItem("teleAction2"));
    contents["teleAction3"] = JSON.parse(localStorage.getItem("teleAction3"));
    contents["teleAction4"] = JSON.parse(localStorage.getItem("teleAction4"));
    contents["autoState"] = JSON.parse(localStorage.getItem("autoState"));
    contents["teleState"] = JSON.parse(localStorage.getItem("teleState"));
    contents["endAuto"] = JSON.parse(localStorage.getItem("endAuto"));

    //get result data
    contents["comments"] = JSON.parse(localStorage.getItem("comments"));

    //get navigation timestamps
    contents["navStamps"] = JSON.parse(localStorage.getItem("navStamps"));
    
    return JSON.stringify(contents);
}

function handleClick() {
    document.getElementById("finishButton").disabled = true;
  }
  
  /** @param {Array.<ScorePiece>} array */
  function trimScoreGrid(array) {
      if (array==null || !array) return [];
      const histories = array.map((scorePiece) => scorePiece.history);
      console.log(histories);
      let rtv = {};
      //store only the indexes that have values
      for (let i in histories) {
        if (Object.keys(histories[i]).length > 0)
          rtv[i] = histories[i];
      }
      return rtv;
    }