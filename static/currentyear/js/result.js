function collectData() {
    let contents = {};
    contents["contentType"] = "match";

    //get home data
    contents["preliminaryData"] = JSON.parse(localStorage.getItem("preliminaryData"));

    //get prematch data
    contents["startObject"] = JSON.parse(localStorage.getItem("startObject"));
    contents["roboPos"] = JSON.parse(localStorage.getItem("roboPos"));
    contents["objectLayout"] = JSON.parse(localStorage.getItem("objectLayout"));

    //get scout data
    contents["autoAction1"] = JSON.parse(localStorage.getItem("autoAction1"));
    contents["autoAction2"] = JSON.parse(localStorage.getItem("autoAction2"));
    contents["autoAction3"] = JSON.parse(localStorage.getItem("autoAction3"));
    contents["autoAction4"] = JSON.parse(localStorage.getItem("autoAction4"));
    contents["action1"] = JSON.parse(localStorage.getItem("action1"));
    contents["action2"] = JSON.parse(localStorage.getItem("action2"));
    contents["action3"] = JSON.parse(localStorage.getItem("action3"));
    contents["action4"] = JSON.parse(localStorage.getItem("action4"));
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
  
  /** @param {Array.<ScoreNote>} array */
  function trimScoreGrid(array) {
      if (array==null || !array) return [];
      const histories = array.map((scoreNote) => scoreNote.history);
      console.log(histories);
      let rtv = {};
      //store only the indexes that have values
      for (let i in histories) {
        if (Object.keys(histories[i]).length > 0)
          rtv[i] = histories[i];
      }
      return rtv;
    }