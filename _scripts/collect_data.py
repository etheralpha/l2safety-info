import utilities


def run_app():
  risk_data = []
  l2_count = 0

  if utilities.use_test_data:
    summary_data = utilities.read_file(f"_data/l2beat_summary.json", context="read_summary_data")
    # utilities.log(summary_data, context="summary_data")
  else:
    summary_data = utilities.fetch("https://l2beat.com/api/scaling/summary",  context="fetch_l2beat_summary", data_type="json")
    if (summary_data["status"] == 200) and (summary_data["data"]["success"] == True):
      summary_data = summary_data["data"]
      utilities.save_to_file(f"_data/l2beat_summary.json", {"epoch":utilities.current_time, "data":summary_data}, context=f"save_summary_data")
      # utilities.log(summary_data, context="summary_data")
    else:
      utilities.report_error("Error: L2Beat summary fetch failed", context="fetch_l2beat_summary")
      return

  # print(summary_data["data"]["data"]["projects"])
  for project_details in summary_data["data"]["data"]["projects"]:
    project = summary_data["data"]["data"]["projects"][project_details]
    print(project)
    # details example
    #   {
    #     "id":"arbitrum",
    #     "name":"Arbitrum One",
    #     "slug":"arbitrum",
    #     "type":"layer2",
    #     "category":"Optimistic Rollup",
    #     "provider":"Arbitrum",
    #     "purposes":[
    #        "Universal"
    #     ],
    #     "isArchived":false,
    #     "isUpcoming":false,
    #     "isUnderReview":false,
    #     "badges":[
    #        {
    #           "category":"Stack",
    #           "name":"Nitro"
    #        },
    #        {
    #           "category":"DA",
    #           "name":"EthereumBlobs"
    #        },
    #        {
    #           "category":"VM",
    #           "name":"WasmVM"
    #        },
    #        {
    #           "category":"Other",
    #           "name":"Governance"
    #        },
    #        {
    #           "category":"Other",
    #           "name":"L3HostChain"
    #        },
    #        {
    #           "category":"VM",
    #           "name":"EVM"
    #        }
    #     ],
    #     "tvl":{
    #        "breakdown":{
    #           "total":13388231113.45,
    #           "ether":3950452687.39,
    #           "stablecoin":4707391645.65,
    #           "associated":2037539828.32
    #        },
    #        "associatedTokens":[
    #           "ARB"
    #        ],
    #        "change7d":-0.026403164144550906
    #     },
    #     "stage":"Stage 1",
    #     "risks":[
    #        {
    #           "name":"Sequencer Failure",
    #           "value":"Self sequence",
    #           "sentiment":"good",
    #           "description":"In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There is a 1d delay on this operation."
    #        },
    #        {
    #           "name":"State Validation",
    #           "value":"Fraud proofs (INT)",
    #           "sentiment":"warning",
    #           "description":"Fraud proofs allow 14 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. There is a 6d 8h challenge period."
    #        },
    #        {
    #           "name":"Data Availability",
    #           "value":"Onchain",
    #           "sentiment":"good",
    #           "description":"All of the data needed for proof construction is published on Ethereum L1."
    #        },
    #        {
    #           "name":"Exit Window",
    #           "value":"7d",
    #           "sentiment":"warning",
    #           "warning":{
    #              "value":"The Security Council can upgrade with no delay.",
    #              "sentiment":"bad"
    #           },
    #           "description":"Non-emergency upgrades are initiated on L2 and go through a 8d delay. Since there is a 1d delay to force a tx (forcing the inclusion in the following state update), users have only 7d to exit. \n    \n  If users post a tx after that time, they would only be able to self propose a state root 12d 17h after the last state root was proposed and then wait for the 6d 8h challenge window, while the upgrade would be confirmed just after the 6d 8h challenge window and the 3d L1 timelock."
    #        },
    #        {
    #           "name":"Proposer Failure",
    #           "value":"Self propose",
    #           "sentiment":"good",
    #           "description":"Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    #        }
    #     ]
    #   },
    
    if project["type"] == "layer2" and project["stage"] != "NotApplicable" and project["isArchived"] == False and project["isUpcoming"] == False:
      l2_count += 1
      project_risk = {
        "id": project["id"],
        "name": project["name"],
        "type": project["category"],
        "stage": { "status": None, "color": None, "score": 0 },
        "state_validation": { "status": None, "color": None, "note": None, "score": 0 },
        "data_availability": { "status": None, "color": None, "note": None, "score": 0 },
        "exit_window": { "status": None, "color": None, "note": None, "score": 0 },
        "sequencer_failure": { "status": None, "color": None, "note": None, "score": 0 },
        "proposer_failure": { "status": None, "color": None, "note": None, "score": 0 },
        "tvl": { "val": 0, "val_total": 0, "str": "0", "str_total": "0", "color": None },
        "checkmarks": 0,
        "score": 0
      }

      # type
      if "rollup" in project["category"].lower():
        project["type"] = "rollup"
      elif "validium" in project["category"].lower():
        project["type"] = "validium"

      # stage, score modifier
      if project["isUnderReview"] == True:
        project_risk["stage"]["status"] = "in review"
        project_risk["stage"]["color"] = "muted"
      else:
        project_risk["stage"]["status"] = project["stage"].lower()
        if project_risk["stage"]["status"] == "stage 0":
          project_risk["stage"]["color"] = "danger"
        elif project_risk["stage"]["status"] == "stage 1":
          project_risk["stage"]["color"] = "warning"
          project_risk["stage"]["score"] += 1.5
          project_risk["score"] += 1.5
        elif project_risk["stage"]["status"] == "stage 2":
          project_risk["stage"]["color"] = "success"
          project_risk["stage"]["score"] += 3
          project_risk["score"] += 3
        else:
          project_risk["stage"]["status"] = "n/a"
          project_risk["stage"]["color"] = "muted"

      # risks, checkmarks, score
      # no risk evaluations if in review
      if project["isUnderReview"] == False:
        for risk in project["risks"]:
          # state_validation
          if risk["name"] == "State Validation":
            project_risk["state_validation"]["status"] = risk["name"]
            project_risk["state_validation"]["color"] = utilities.get_risk_color(risk["sentiment"])
            if "warning" in risk:
              project_risk["state_validation"]["note"] = f"{risk['value']}: {risk['warning']['value']} {risk['description']}"
            else:
              project_risk["state_validation"]["note"] = f"{risk['value']}: {risk['description']}"
            project_risk["state_validation"]["score"] = utilities.get_risk_score(risk["sentiment"])
            if project_risk["state_validation"]["color"] == "white":
              project_risk["checkmarks"] += 1
            project_risk["score"] += project_risk["state_validation"]["score"]
          # data_availability
          elif risk["name"] == "Data Availability":
            project_risk["data_availability"]["status"] = risk["name"]
            project_risk["data_availability"]["color"] = utilities.get_risk_color(risk["sentiment"])
            if "warning" in risk:
              project_risk["data_availability"]["note"] = f"{risk['value']}: {risk['warning']['value']} {risk['description']}"
            else:
              project_risk["data_availability"]["note"] = f"{risk['value']}: {risk['description']}"
            project_risk["data_availability"]["score"] = utilities.get_risk_score(risk["sentiment"])
            if project_risk["data_availability"]["color"] == "white":
              project_risk["checkmarks"] += 1
            project_risk["score"] += project_risk["data_availability"]["score"]
          # exit_window
          elif risk["name"] == "Exit Window":
            project_risk["exit_window"]["status"] = risk["name"]
            project_risk["exit_window"]["color"] = utilities.get_risk_color(risk["sentiment"])
            if "warning" in risk:
              project_risk["exit_window"]["note"] = f"{risk['value']}: {risk['warning']['value']} {risk['description']}"
            else:
              project_risk["exit_window"]["note"] = f"{risk['value']}: {risk['description']}"
            project_risk["exit_window"]["score"] = utilities.get_risk_score(risk["sentiment"])
            if project_risk["exit_window"]["color"] == "white":
              project_risk["checkmarks"] += 1
            project_risk["score"] += project_risk["exit_window"]["score"]
          # sequencer_failure
          elif risk["name"] == "Sequencer Failure":
            project_risk["sequencer_failure"]["status"] = risk["name"]
            project_risk["sequencer_failure"]["color"] = utilities.get_risk_color(risk["sentiment"])
            if "warning" in risk:
              project_risk["sequencer_failure"]["note"] = f"{risk['value']}: {risk['warning']['value']} {risk['description']}"
            else:
              project_risk["sequencer_failure"]["note"] = f"{risk['value']}: {risk['description']}"
            project_risk["sequencer_failure"]["score"] = utilities.get_risk_score(risk["sentiment"])
            if project_risk["sequencer_failure"]["color"] == "white":
              project_risk["checkmarks"] += 1
            project_risk["score"] += project_risk["sequencer_failure"]["score"]
          # proposer_failure
          elif risk["name"] == "Proposer Failure":
            project_risk["proposer_failure"]["status"] = risk["name"]
            project_risk["proposer_failure"]["color"] = utilities.get_risk_color(risk["sentiment"])
            if "warning" in risk:
              project_risk["proposer_failure"]["note"] = f"{risk['value']}: {risk['warning']['value']} {risk['description']}"
            else:
              project_risk["proposer_failure"]["note"] = f"{risk['value']}: {risk['description']}"
            project_risk["proposer_failure"]["score"] = utilities.get_risk_score(risk["sentiment"])
            if project_risk["proposer_failure"]["color"] == "white":
              project_risk["checkmarks"] += 1
            project_risk["score"] += project_risk["proposer_failure"]["score"]
          else:
            utilities.report_error(f"Error: Unknown risk {risk['name']} for {project['id']}", context="set_project_risks")

      # tvl
      project_risk["tvl"]["val"] = project["tvl"]["breakdown"]["total"] - project["tvl"]["breakdown"]["associated"]
      project_risk["tvl"]["val_total"] = project["tvl"]["breakdown"]["total"]
      project_risk["tvl"]["str"] = utilities.convert_tvl(project_risk["tvl"]["val"])
      project_risk["tvl"]["str_total"] = utilities.convert_tvl(project_risk["tvl"]["val_total"])
      project_risk["tvl"]["color"] = utilities.get_tvl_color(project_risk["tvl"]["val"])

      risk_data.append(project_risk)


  # save all data
  if not utilities.use_test_data:
    utilities.save_to_file(f"_data/l2safety_uncleaned.json", {"epoch":utilities.current_time, "data":risk_data}, context=f"save_risk_data")


  # clean data
  # remove if doesn't have at least 1 checkmark
  risk_data = [project for project in risk_data if (project["checkmarks"] > 0 or project["stage"]["status"] == "in review")]
  # sort by score then by tvl
  # risk_data = sorted(risk_data, key=lambda project: (project["score"], project["tvl"]["val"]), reverse=True)
  # sort by tvl then by score
  risk_data = sorted(risk_data, key=lambda project: (project["tvl"]["val"], project["score"]), reverse=True)


  # save filtered/sorted data
  if not utilities.use_test_data:
    utilities.save_to_file(f"_data/l2safety.json", {"epoch":utilities.current_time, "data":risk_data}, context=f"save_risk_data")
  # utilities.pprint(risk_data)
  print(risk_data)
  print(f"L2 count: {l2_count}")

      


run_app()
print(f"Error count: {utilities.error_count}")

