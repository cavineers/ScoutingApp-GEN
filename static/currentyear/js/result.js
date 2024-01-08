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
    //scoreGrid: just array of ScoreNode.history    =   [ScoreNode, ScoreNode, ...] -> [ScoreNode.history, ...]
    contents["scoreGrid"] = trimScoreGrid(JSON.parse(localStorage.getItem("scoreGrid")));
    contents["pickUps"] = JSON.parse(localStorage.getItem("pickUps"));
    contents["shelfPickUps"] = JSON.parse(localStorage.getItem("shelfPickUps"));
    contents["objectDrops"] = JSON.parse(localStorage.getItem("objectDrops"));
    contents["defenses"] = JSON.parse(localStorage.getItem("defenses"));
    contents["autoChargeState"] = JSON.parse(localStorage.getItem("autoChargeState"));
    contents["chargeState"] = JSON.parse(localStorage.getItem("chargeState"));
    contents["endAuto"] = JSON.parse(localStorage.getItem("endAuto"));
    //get result data
    contents["comments"] = JSON.parse(localStorage.getItem("comments"));
    //get navigation timestamps
    contents["navStamps"] = JSON.parse(localStorage.getItem("navStamps"));
    return JSON.stringify(contents);
}

/** @param {Array.<ScoreNode>} array */
function trimScoreGrid(array) {
    if (array==null || !array) return [];
    const histories = array.map((scoreNode) => scoreNode.history);
    console.log(histories);
    let rtv = {};
    //store only the indexes that have values
    for (let i in histories) {
      if (Object.keys(histories[i]).length > 0)
        rtv[i] = histories[i];
    }
    return rtv;
  }