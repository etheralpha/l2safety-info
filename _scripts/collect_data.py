import utilities


def run_app():
  risk_data = []
  projects = set()

  if utilities.use_test_data:
    projects = {'arbitrum', 'optimism', 'real', 'eclipse'}
    # projects = {'fraxtal', 'rhinofi', 'wirex', 'ancient8', 'paradex', 'linea', 'kroma', 'astarzkevm', 'gpt', 'edgeless', 'zksync-lite', 'aevo', 'fuelv1', 'alienx', 'base', 'sxnetwork', 'starknet', 'rss3', 'orderly', 'xterio', 'scroll', 'polygonzkevm', 'mode', 'optimism', 'bob', 'xlayer', 'metal', 'zora', 'hypr', 'kinto', 'karak', 'apex', 'bobanetwork', 'termstructure', 'mantapacific', 'lambda', 'publicgoodsnetwork', 'taiko', 'blast', 'lisk', 'swan', 'cronoszkevm', 'aleph-zero', 'witness', 'zkfair', 'patex', 'derive', 'redsonic', 'real', 'optopia', 'zksync-era', 'metis', 'zkspace', 'arbitrum', 'nova', 'tanx', 'dydx', 'myria', 'mantle', 'silicon', 'mint', 'immutablex', 'zircuit', 'loopring', 'sorare', 'cartesi-honeypot', 'hychain', 'eclipse', 'parallel', 'redstone', 'degate3', 'reya', 'galxegravity', 'cyber'}
  else:
    dashboard_source = utilities.fetch("https://l2beat.com/scaling/summary",  context="fetch_dashboard_source", data_type="text")["data"]
    for item in dashboard_source.split('href="/scaling/projects/'):
      projects.add(item.split('#')[0].split('"')[0])
    projects.remove("<!DOCTYPE html><html lang=")


  for project in projects:
    print(project)
    project_risk = {
      "name": project,
      "stage": None,
      "layer": "L2",
      "state_validation": { "status": None, "color": None, "score": 0 },
      "data_availability": { "status": None, "color": None, "score": 0 },
      "exit_window": { "status": None, "color": None, "score": 0 },
      "sequencer_failure": { "status": None, "color": None, "score": 0 },
      "proposer_failure": { "status": None, "color": None, "score": 0 },
      "checkmarks": 0,
      "score": 0
    }
    source_url = f"https://l2beat.com/scaling/projects/{project}"
    project_source = utilities.fetch(source_url,  context="fetch_project_source", data_type="text")["data"]

    # stage, layer
    # no stage if it's an L3
    if "id=\"stage\"" in project_source:
      stage = project_source.split("id=\"stage\"")[1].split("</span></span>")[0].split(">")[-1]
      project_risk["stage"] = stage
    else:
      project_risk["stage"] = "-"
      project_risk["layer"] = "L3"

    # risks, checkmarks, score
    # no risk evaluations if in review
    if project_risk["stage"].lower() != "in review":
      # state_validation
      if ">State validation</h3>" in project_source:
        project_risk["state_validation"]["status"] = project_source.split(">State validation</h3>")[1].split("</span>")[0].split(">")[-1]
        project_risk["state_validation"]["color"] = utilities.get_risk_color(project_source.split(">State validation</h3>")[1])
        project_risk["state_validation"]["score"] = utilities.get_risk_score(project_risk["state_validation"]["color"])
        if project_risk["state_validation"]["color"] == "white":
          project_risk["checkmarks"] += 1
        project_risk["score"] += project_risk["state_validation"]["score"]
      # data_availability
      if ">Data availability</h3>" in project_source:
        project_risk["data_availability"]["status"] = project_source.split(">Data availability</h3>")[1].split("</span>")[0].split(">")[-1]
        project_risk["data_availability"]["color"] = utilities.get_risk_color(project_source.split(">Data availability</h3>")[1])
        project_risk["data_availability"]["score"] = utilities.get_risk_score(project_risk["data_availability"]["color"])
        if project_risk["data_availability"]["color"] == "white":
          project_risk["checkmarks"] += 1
        project_risk["score"] += project_risk["data_availability"]["score"]
      # exit_window
      if ">Exit window</h3>" in project_source:
        project_risk["exit_window"]["status"] = project_source.split(">Exit window</h3>")[1].split("</span>")[0].split(">")[-1]
        project_risk["exit_window"]["color"] = utilities.get_risk_color(project_source.split(">Exit window</h3>")[1])
        project_risk["exit_window"]["score"] = utilities.get_risk_score(project_risk["exit_window"]["color"])
        if project_risk["exit_window"]["color"] == "white":
          project_risk["checkmarks"] += 1
        project_risk["score"] += project_risk["exit_window"]["score"]
      # sequencer_failure
      if ">Sequencer failure</h3>" in project_source:
        project_risk["sequencer_failure"]["status"] = project_source.split(">Sequencer failure</h3>")[1].split("</span>")[0].split(">")[-1]
        project_risk["sequencer_failure"]["color"] = utilities.get_risk_color(project_source.split(">Sequencer failure</h3>")[1])
        project_risk["sequencer_failure"]["score"] = utilities.get_risk_score(project_risk["sequencer_failure"]["color"])
        if project_risk["sequencer_failure"]["color"] == "white":
          project_risk["checkmarks"] += 1
        project_risk["score"] += project_risk["sequencer_failure"]["score"]
      # proposer_failure
      if ">Proposer failure</h3>" in project_source:
        project_risk["proposer_failure"]["status"] = project_source.split(">Proposer failure</h3>")[1].split("</span>")[0].split(">")[-1]
        project_risk["proposer_failure"]["color"] = utilities.get_risk_color(project_source.split(">Proposer failure</h3>")[1])
        project_risk["proposer_failure"]["score"] = utilities.get_risk_score(project_risk["proposer_failure"]["color"])
        if project_risk["proposer_failure"]["color"] == "white":
          project_risk["checkmarks"] += 1
        project_risk["score"] += project_risk["proposer_failure"]["score"]
    risk_data.append(project_risk)


  # clean data
  # remove if not an L2
  risk_data = [project for project in risk_data if project["layer"] == "L2"]
  # remove if doesn't have at least 1 checkmark
  risk_data = [project for project in risk_data if (project["checkmarks"] > 0 or project["stage"].lower() == "in review")]
  # sort by score
  risk_data = sorted(risk_data, key=lambda project: project['score'], reverse=True)


  # save data
  if not utilities.use_test_data:
    utilities.save_to_file(f"_data/l2safety.json", {"epoch":utilities.current_time, "data":risk_data}, context=f"save_risk_data")
  # utilities.pprint(risk_data)
  print(risk_data)
  print(f"Project count: {len(risk_data)}")

      


run_app()
print(f"Error count: {utilities.error_count}")

