<?php
include_once("assist.php");
include_once("help_log_display.php");
include_once("db_helper.php");

$error = NULL;
$rc = OK;
$type_enum = "error";
$reporter_enum = "ji";
$bug_reporter_unique_ref = NULL;
$regex_profile = NULL;
$show_numbers = False;

//echo get_keys_as_string($_GET);

$expected_get_keys = array("arch", "attach_id", "crash_known_id", "end", "exec", "exec_path", "lm_id", "lm_type",
						   "lm_type_id", "params", "project", "result", "start", "sub_type", "sub_type_id", "suite",
						   "target", "test_exec_id", "test_name", "test_root_id", "test_suite_root_id", "variant");



foreach($expected_get_keys as $key){

	if (isset($_GET[$key]) == False){
		$rc = ERROR_INVALID_PARAM;
		echo $key." is missing from the URL";
	}
}

gen_head("Proj: ".$_GET["project"]." Reg: ".$_GET["exec"]." LM: ".$_GET["lm_id"], "style.css");

if (isset($_GET["sl"])) {
	$show_numbers = ' | ';
}

if (isset($_GET["type_enum"])){
	$type_enum = $_GET["type_enum"];
}

if (isset($_GET["reporter_enum"])){
	$reporter_enum = $_GET["reporter_enum"];
}

if (isset($_GET["bug_reporter_unique_ref"])){
	$bug_reporter_unique_ref = $_GET["bug_reporter_unique_ref"];
}

if ($rc == OK) {

	$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

	if ($sql_handle != NULL) {

		$test_profile = array();
		$rc =  get_log_and_crash_profile($error, $sql_handle, $_GET["lm_id"], $test_profile);

		if ($rc == OK) {

			echo "<center><h3>".$_GET["target"]."-".$_GET["arch"]."-".$_GET["variant"]." --- ".$_GET["exec_path"]."/".$_GET["test_name"]."".$_GET["params"];

			if (intval($_GET["crash_known_id"])> 0) {
				echo " (Known Crash)";
			}

			echo "<h3></center>";

			$marked_lines = array();
			/*$marked_lines[0] = array("start"=> 14438, "end"=>14445, "mark"=>"=");
			$marked_lines[1] = array("start"=> 14433, "end"=>14450, "mark"=>">");
	*/

			$line_count = count($test_profile["log"]["file_data"]["lines"]);

			$line_count = min($line_count, 30);

			marked_lines_show($test_profile["log"]["file_data"]["lines"], "Test Log", $marked_lines, $line_count, 140, $show_numbers, TRUE);

			echo "TODO: Put download for partial and full log here link here.";

			if (array_key_exists("header", $test_profile["crash"])){
				show($test_profile["crash"]["header"],"GDB Header", $line_count, 140, TRUE);
			}

			if (array_key_exists("back_trace", $test_profile["crash"])){
				show($test_profile["crash"]["back_trace"],"Back Trace", $line_count, 140, TRUE);
			}

			if (array_key_exists("info_reg_data", $test_profile["crash"])){
				show($test_profile["crash"]["info_reg_data"],"Info Reg", $line_count, 140, TRUE);
			}

			if (array_key_exists("display", $test_profile["crash"])){
				show($test_profile["crash"]["display"],"Display", $line_count, 140, TRUE);
			}

			$line_count = min(count($test_profile["crash"]["lines"]), 10);

			$crash_profile_lines = implode("\n", $test_profile["crash"]["lines"]);

			show($crash_profile_lines,"Crash Profile", $line_count, 140, TRUE);


			$regex = NULL;
			$type_enum = NULL;
			$recorder_enum = NULL;
			$unique_ref = NULL;
			$readonly = False;

			$other_patterns = array();

			$rc = check_handle_sumbit($error, $sql_handle, $crash_profile_lines);

			if ($rc == OK){
				$type = $_GET["lm_type"];

				if ($_GET["lm_type"] == "process_seg") {
					$type = $_GET["sub_type"];
				}
				$crash_type_id = get_crash_type_id($error, $sql_handle, $_GET["project"], $type);

				if ($crash_type_id <= 0) {
					$rc = $crash_type_id;
				}
			}


			#Check to see if this page is updated on a submit:
			if (isset($_GET["submit"])){
				#Check to see if the user hit the use button
				if ($_GET["submit"] == "Use"){
					# if they did then use the known regex profile.
					$_GET["regex"] = $_GET["known_regex"];
				}
			}


			if ($rc == OK){
				if (isset($_GET["regex"])){
					$regex = $_GET["regex"];
					$type_enum = $_GET["type_enum"];
					$recorder_enum = $_GET["recorder_enum"];
					$unique_ref = $_GET["unique_ref"];
				}
				else {
					# Check to see if this is a known crash being display
					if (intval($_GET["crash_known_id"])> 0) {

						# if it is a known crash then do the following.
						$rows = array();
						$where = array(	"crash_known_id"=> $_GET["crash_known_id"]);

						$rc = get_crash_known_with_bug_info($error, $sql_handle, $rows, $where);

						if ($rc == OK) {
							if (count($rows) > 0) {

								$regex = $rows[0]["regex"];
								$type_enum = $rows[0]["type_enum"];
								$recorder_enum = $rows[0]["recorder_enum"];
								$unique_ref = $rows[0]["unique_ref"];
							}
							else{
								$rc = ERROR_GENERAL;
								$error = "No known crash found!";
							}
						}
					}
					else {
						$regex = $test_profile["crash"]["regex"];
					}
				}

				if (intval($_GET["crash_known_id"]) <= 0) {
					/* Query the database and see if there are any other crash regex of this type for this test */
					/* reminder that we don't need to query by project here because the crash types are project specific */
					$rows = array();
					$where = array("fk_crash_type_id"=> intval($crash_type_id),
								   "fk_test_root_id" => intval($_GET["test_root_id"]));

					$rc = get_crash_known_with_bug_info($error, $sql_handle, $other_patterns, $where);
				}
			}

			if ($rc == OK) {
				echo '<form>';
				dup_get_input_for_form(array("regex", "type_enum", "recorder_enum", "unique_ref", "button_index", "submit", "crash_type_id", "crash_exec_ids", "crash_exec_ids[]"));
				echo '<input type=hidden name="crash_type_id" value='.$crash_type_id.' >';

				$match_check = False;

				echo "<BR>";

				echo "<center><strong>Regex Profile ";

				if (check_regex($regex, $crash_profile_lines, $error)) {
					$match_check = True;
					echo "[Match]";
				}
				else{
					echo "[No Match]";
				}

				if ($readonly){
					echo " ReadOnly";
				}

				echo "</strong></center>";


				echo '<table align="center" width=50%>';

				echo '<tr>';

				echo '<td>';
				echo '&nbsp';
				echo '</td>';

				echo '<td align="center" >';
				$type_enums = array("error", "generated");

				echo '<label>Crash Type: <label><select name="type_enum">';
				foreach($type_enums as $value){
					if ($value == $type_enum){
						echo '<option value="'.$value.'" selected>'.$value."</option>";
					}
					else{
						echo '<option value="'.$value.'" >'.$value."</option>";
					}
				}
				echo '</select>';
				echo '</td>';

				$recorder_enum = array("ji", "pr");

				echo '<td align="center" >';
				echo '<label>Reporter Type: <label><select name="recorder_enum">';
				foreach($recorder_enum as $value){
					if ($value == $recorder_enum){
						echo '<option value="'.$value.'" selected>'.$value."</option>";
					}
					else{
						echo '<option value="'.$value.'" >'.$value."</option>";
					}
				}
				echo '</select>';
				echo '</td >';

				echo '<td align="center" >';

				if ($unique_ref != NULL) {
					echo '<label>Unique Ref: </label><input type=text name="unique_ref" value="'.$unique_ref.'" >';
				}
				else{
					echo '<label>Unique Ref: </label><input type=text name="unique_ref">';
				}

				echo '</td>';

				echo '<td>';
				echo '&nbsp';
				echo '</td>';

				echo '</tr>';

				echo '<tr>';
				echo '<td colspan="5">';

				if ($readonly){
					echo '<textarea name="regex" cols=140 rows='.$line_count.' readonly>';
				}
				else {
					echo '<textarea name="regex" cols=140 rows='.$line_count.' >';
				}

				echo $regex;
				echo '</textarea>';
				echo '</td>';
				echo '</tr>';

				echo '<tr>';


				echo '<td>';
				echo '&nbsp';
				echo '</td>';

				echo '<td align="center">';
				echo '<input type="submit" name="submit" value="Test Change" >';
				echo '</td>';

				if ($match_check){
					if (intval($_GET["crash_known_id"])> 0) {
						echo '<td align="center">';
						echo '<input type="submit" name="submit" value="Update Regex" >';
						echo '</td>';
					}
					else {
						echo '<td align="center">';
						echo '<input type="submit" name="submit" value="Apply" >';
						echo '</td>';
					}
				}
				else{
						echo '<td align="center">';
						echo '&nbsp';
						echo '</td>';
				}

				echo '<td>';
				echo '&nbsp';
				echo '</td>';

				echo '<td>';
				echo '&nbsp';
				echo '</td>';

				echo '</tr>';

				echo '<table align="center" width="20%">';
				echo '</form>';

				#========================================================================================

				echo '<form>';
				dup_get_input_for_form(array("regex", "type_enum", "recorder_enum", "unique_ref", "button_index", "other_crash_known_id", "submit", "crash_type_id", "crash_exec_ids", "crash_exec_ids[]"));

				$max_other_patterns = count($other_patterns);

				if ($max_other_patterns > 0) {
					$button_index = 1;
					if (isset($_GET["button_index"])){
						$button_index = $_GET["button_index"];
					}

					$other_pattern_index = $button_index -1;

					echo '<table align="center">';
					echo '<input type=hidden name="other_crash_known_id" value='.$other_patterns[$other_pattern_index]["crash_known_id"].' >';
					echo '<input type=hidden name="type_enum" value='.$other_patterns[$other_pattern_index]["type_enum"].' >';
					echo '<input type=hidden name="recorder_enum" value='.$other_patterns[$other_pattern_index]["recorder_enum"].' >';
					echo '<input type=hidden name="unique_ref" value='.$other_patterns[$other_pattern_index]["unique_ref"].' >';
					echo '<input type=hidden name="crash_type_id" value='.$crash_type_id.' >';

					$match_check = False;

					echo '<tr>';
					echo '<td colspan=3>';


					if (check_regex($other_patterns[$other_pattern_index]["regex"], $crash_profile_lines, $error)) {
						$match_check = True;
						echo "<center><strong>Known Regex Profile [Match] (".$button_index." of ".$max_other_patterns.") [".$other_patterns[$other_pattern_index]["crash_known_id"]."]</strong></center>";
					}
					else{
						echo "<center><strong>Known Regex Profile [No Match] (".$button_index." of ".$max_other_patterns.") [".$other_patterns[$other_pattern_index]["crash_known_id"]."]</strong></center>";
					}

					echo '<center><textarea name="known_regex" cols=140 rows='.$line_count.' readonly>';
					echo $other_patterns[$other_pattern_index]["regex"];
					echo '</textarea></center>';
					echo '</td>';
					echo '</tr>';

					echo '<tr>';
					echo '<td align="left" width="33%">';
					if ($button_index > 1) {
						echo '<input  type="submit" name="button_index" value='.($button_index -1).' \>';
					}
					else{
						echo "&nbsp";
					}
					echo '</td>';

					echo '<td align="center" width="33%">';
					if ($match_check){
						echo '<input  type="submit" name="submit" value="Use" \>';
					}
					else{
						echo "&nbsp";
					}

					echo "&nbsp";
					echo '</td>';

					echo '<td align="right" width="33%">';

					if ($button_index < $max_other_patterns) {
						echo '<input  type="submit" name="button_index" value='.($button_index +1).' \>';
					}
					else{
						echo "&nbsp";
					}
					echo '</td>';
					echo '</tr>';

					echo '</table>';
					echo '</form>';
				}
			}
		}
	}

	if ($rc != OK){
		echo "<center>".$error."</center><BR>";
	}
}


function look_for_orphans(&$error, $sql_handle, $crash_known_id){
	$rc = OK;
	$orphan_rows = array();

	$select = array("crash_exec_id", "line_marker_id", "fk_test_root_id", "target.name as target", "arch.name as arch", "variant_root.variant as variant");

	$tables = array("crash_exec", "line_marker", "test_exec", "test_revision", "variant_exec", "variant_root", "target", "arch");

	$where = array("crash_exec.fk_line_marker_id"=>"line_marker.line_marker_id",
				   "line_marker.fk_test_exec_id"=>"test_exec.test_exec_id",
				   "test_exec.fk_test_revision_id"=>"test_revision.test_revision_id",
					"test_exec.fk_variant_exec_id"=>"variant_exec.variant_exec_id",
					"variant_exec.fk_variant_root_id"=>"variant_root.variant_root_id",
					"variant_root.fk_target_id"=>"target.target_id",
					"variant_root.fk_arch_id"=>"arch.arch_id",

				   # for the same test root id
				   "test_revision.fk_test_root_id" => $_GET["test_root_id"],
				   # set the following to only get crash of the same type..
				   "line_marker.fk_line_marker_type_id" => $_GET["lm_type_id"],
				   "line_marker.fk_line_marker_sub_type_id" => $_GET["sub_type_id"]
					);

	$where_string = "crash_exec.fk_crash_known_id IS NULL";

	$rc = select($error, $sql_handle, $orphan_rows, $tables, $select,  $where, $where_string);

	if($rc == OK){
		# get the profile for each orphan and compare it to the regex..
		$track_matching_orphans = array();
		foreach($orphan_rows as $orphan) {
			$test_profile = array();
			$rc = get_log_and_crash_profile($error, $sql_handle, $orphan["line_marker_id"], $test_profile);

			if ($rc == OK)
			{
				if(count($test_profile["crash"]["lines"]) > 0) {

					$crash_profile = implode("\n",$test_profile["crash"]["lines"]);

					if (check_regex($_GET["regex"], $crash_profile, $local_error)) {
						$track_matching_orphans[count($track_matching_orphans)] = $orphan;

						if (count($track_matching_orphans) >= 50){
							break;
						}
					}
				}
			}
			else{
				break;
			}

		} // end of foreach($orphan_rows as $orphans) {

		if ($rc == OK){

			if (count($track_matching_orphans) > 0) {

				$the_string = dup_get_to_string(array("lm_id", "crash_known_id", "submit", "crash_exec_ids",  "crash_exec_ids[]"));

				echo "<BR><center><strong>Found Orphans Matching this Regex</strong></center>";
				echo '<form>';
				dup_get_input_for_form(array("submit", "known_crash_id", "crash_exec_ids", "crash_exec_ids", "crash_exec_ids[]"));

				echo '<input type="hidden" name="known_crash_id" value='.$crash_known_id.'  >';

				echo '<table align=center border=2>';
				echo '<tr>';

				echo '<th>';
				echo "Select";
				echo '</th>';

				echo '<th>';
				echo "Link";
				echo '</th>';

				echo '<th>';
				echo "Target";
				echo '</th>';

				echo '<th>';
				echo "Arch";
				echo '</th>';

				echo '<th>';
				echo 'Variant';
				echo '</th>';

				echo '</tr>';

				foreach($track_matching_orphans as $tracked_orphan) {
					echo '<tr>';
					echo '<td align="center" >';
					echo '<input type=checkbox name="crash_exec_ids[]" value='.$tracked_orphan["crash_exec_id"].' checked>';
					echo '</td>';

					echo '<td>';
					echo '<a href="./crash_view.php?lm_id='.$tracked_orphan["line_marker_id"]."&crash_known_id=&".$the_string.'">'.$tracked_orphan["line_marker_id"]."</a>";
					echo '</td>';

					echo '<td>';
					echo $tracked_orphan["target"];
					echo '</td>';

					echo '<td>';
					echo $tracked_orphan["arch"];
					echo '</td>';

					echo '<td>';
					echo $tracked_orphan["variant"];
					echo '</td>';
					echo '</tr>';
				}

				echo '</table>';
				echo '<center><input type=submit name="submit" value="Adopt Selected Orphans"></center>';
				echo '</form>';
			}
		}
	}
	return $rc;
}


function check_handle_sumbit(&$error, $sql_handle, $crash_profile){
	$rc = OK;
	$local_error = "";

	if (isset($_GET["submit"])) {
		$regex = NULL;
		$type_enum = NULL;
		$recorder_enum = NULL;
		$unique_ref = NULL;
		$fk_project_bug_id = NULL;

		if (isset($_GET["regex"])){
			$regex = $_GET["regex"];
		}

		if (isset($_GET["type_enum"])){
			$type_enum = $_GET["type_enum"];
		}

		if (isset($_GET["recorder_enum"])){
			$recorder_enum = $_GET["recorder_enum"];
		}

		if (isset($_GET["unique_ref"])){
			$unique_ref = $_GET["unique_ref"];
		}

		if (check_regex($_GET["regex"], $crash_profile, $local_error)) {
			if ($_GET["submit"] == "Apply") {

				$fk_project_bug_id = NULL;
				# check to see if if the type_enum of this bug is error or generated
				if ($type_enum != NULL){
					if ($type_enum == "error"){
						if ($recorder_enum != NULL) {
							if (strlen($unique_ref) <= 0){
								$rc = ERROR_GENERAL;
								$error = __FUNCTION__.":".__LINE__." A bug tracking refernce must be provided if the crash is not generated on purpose";
							}
							else{
								$fk_project_bug_id = add_project_bug($error, $sql_handle, $recorder_enum, $unique_ref, $_GET["project"], $summary=NULL, $comment=NULL, $added_by="other");

								if ($fk_project_bug_id < 0){
									$rc = $fk_project_bug_id;
								}
							}
						}
						else{
							$rc = ERROR_GENERAL;
							$error = __FUNCTION__.":".__LINE__." Form recorder_eum was unexpectedly NULL";
						}
					}
				}
				else{
					$rc = ERROR_GENERAL;
					$error = __FUNCTION__.":".__LINE__." Form status was unexpectedly NULL";
				}

				if ($rc == OK) {
					# write this in as a known regex now
					$insert_dict = array("fk_crash_type_id"=>$_GET["crash_type_id"],
						                 "fk_test_root_id"=>$_GET["test_root_id"],
										 "fk_test_suite_root_id"=>$_GET["test_suite_root_id"],
										 "type_enum"=>$type_enum,
										 "regex"=>'compress("'.addslashes($_GET["regex"]).'")',
										 "created"=>"now()"
										 );

					if ($fk_project_bug_id != NULL){
						$insert_dict["fk_project_bug_id"] = $fk_project_bug_id;
					}

					$rc = insert($error, $sql_handle, "crash_known", $insert_dict, FALSE);

					if ($rc > 0) {
						$crash_known_id = $rc;
						$_GET["crash_known_id"] = $rc;

						$where = array();
						$update = array("fk_crash_known_id"=>$rc);
						$where = array("fk_line_marker_id"=>$_GET["lm_id"]);

						# then update the crash that generated this regex
						$rc = update($error, $sql_handle, "crash_exec", $update, $where);

						if ($rc == OK) {
							$rc = look_for_orphans($error, $sql_handle, $crash_known_id);
						}
					}
				}
			}
			else if ($_GET["submit"] == "Adopt Selected Orphans") {
				#Adopt  all the children then see if there are others..

				if(isset($_GET["crash_exec_ids"])){
					foreach($_GET["crash_exec_ids"] as $crash_exec_id_index){
						$where = array();
						$update = array("fk_crash_known_id"=>$_GET["crash_known_id"]);
						$where = array("crash_exec_id"=>$crash_exec_id_index);

						# then update the crash that generated this regex
						$rc = update($error, $sql_handle, "crash_exec", $update, $where);

						if ($rc != OK){
							break;
						}
					}

					if ($rc == OK) {
						echo '<center>So kind of you to take in ('.count($_GET["crash_exec_ids"]).') lost children.</center>';
						$rc = look_for_orphans($error, $sql_handle, $_GET["known_crash_id"]);
					}
				}
				else{
					$rc = ERROR_GENERAL;
					$error = __FUNCTION__.":".__LINE__."$_GET is missing expected key crash_exec_ids";
				}
			}
			else if ($_GET["submit"] == "Use") {
				# Only update this test to use this regex.
				$update = array("fk_crash_known_id"=>$_GET["other_crash_known_id"]);
				$where = array("fk_line_marker_id"=>$_GET["lm_id"]);

				# Then update the crash that generated this regex
				$rc = update($error, $sql_handle, "crash_exec", $update, $where);

			}
			else if ($_GET["submit"] == "Update Regex") {

				# Check to see how many crashes reference this same crash ID
				$rows=array();
				$select=array("crash_exec_id", "fk_line_marker_id");
				$tables=array("crash_exec");
				$where=array("crash_exec.fk_crash_known_id"=>$_GET["crash_known_id"],
							 "crash_exec.fk_line_marker_id!"=>$_GET["lm_id"],);

				$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

				if ($rc == OK) {

					$update_is_ok = 0;

					$check_count = 0;
					$max_time = (30 * 1000000); // 30 seconds

					$start_time = microtime(true);

					$rows_count = count($rows);

					$min_check = min(10, $rows_count);
					$max_check = min($min_check + 10, $rows_count);

					foreach($rows as $row) {

						$test_profile = array();
						$rc = get_log_and_crash_profile($error, $sql_handle, $row["fk_line_marker_id"], $test_profile);

						if ($rc == OK)
						{
							if(count($test_profile["crash"]["lines"]) > 0) {

								$crash_profile = implode("\n",$test_profile["crash"]["lines"]);

								if (check_regex($_GET["regex"], $crash_profile, $local_error)) {
									$check_count = $check_count + 1;
								}
								else{
									$update_is_ok = $row["fk_line_marker_id"];
									break;
								}
							}
						}
						else{
							break;
						}

						if ($check_count > $max_check){
							break;
						}

						if ((microtime(true)-  $start_time) > $max_time){
							break;
						}
					} // end of foreach($rows as $row) {

					if ($rc == OK){
						if($update_is_ok == 0) {
							if ($check_count >= $min_check ){

								$update = array("regex"=>'compress("'.addslashes($_GET["regex"]).'")');
								$where = array("crash_known_id"=>$_GET["crash_known_id"]);

								# Then update the regex for the crash_known_id
								$rc = update($error, $sql_handle, "crash_known", $update, $where);

								if ($rc == OK){
									$rc = look_for_orphans($error, $sql_handle, $_GET["crash_known_id"]);
								}
							}
							else{
								$rc = ERROR_GENERAL;
								$error = __FUNCTION__.":".__LINE__." The minimum number of checks(".$min_check .", completed ".$check_count.") could not be accomplished in time";
							}
						}
						else{
							$rc = ERROR_GENERAL;
							$error = __FUNCTION__.":".__LINE__." New pattern did not match crash profile for line_marker_id: ".$Update_is_ok;
						}
					}
				}
			}
		}
		else{
			echo $local_error;
			$error = $local_error;
			$rc = ERROR_GENERAL;
		}
	}
	return $rc;
}

function generate_shutdown_crash_profile(&$error, &$log_lines, &$crash_profile, $start, &$end){
	$rc = OK;
	$crash_profile["lines"] = array();
	$crash_profile["regex"] = array();
	$max_lines = count($log_lines);


	$crash_profile["lines"][$start] = $log_lines[$start];

	for($index =  $start+1; $index < $max_lines; $index ++) {

		$pos = strpos($log_lines[$index],']ASPACE');

		if ($pos !== FALSE){
			$crash_profile["lines"][$index] = $log_lines[$index];
		}

		$pos = strpos($log_lines[$index],'x86_64 context[');

		if ($pos !== FALSE){
			$crash_profile["lines"][$index] = $log_lines[$index];
		}

		$pos = strpos($log_lines[$index],'instruction[');

		if ($pos !== FALSE){
			$crash_profile["lines"][$index] = $log_lines[$index];
		}

		$pos = strpos($log_lines[$index],'stack[');

		if ($pos !== FALSE){
			$crash_profile["lines"][$index] = $log_lines[$index];
		}

	}

	if ($rc == OK){
		$crash_profile["regex"] = preg_quote(implode("\n",$crash_profile["lines"]));
		$crash_profile["regex"] = preg_replace("/[[:blank:]]+/", "\s*", $crash_profile["regex"]);
		$crash_profile["regex"] = preg_replace("/PID\\\=\d+/", "PID=\d+", $crash_profile["regex"]);
		$crash_profile["regex"] = preg_replace("/PF\\\=\d+/", "PF=\d+", $crash_profile["regex"]);
		$crash_profile["regex"] = preg_replace("/\[\d+/", "[\d+", $crash_profile["regex"]);
	}

	return $rc;
}

function generate_kdump_crash_profile(&$error, $sql_handle, &$log_lines, &$crash_profile) {
	global $qnx_tool_path;
	# first pull the kudmp information from the log file.
	$kdump_lines = array_splice($log_lines, $crash_profile["line_marker_info"]["start"] - key($log_lines), ($crash_profile["line_marker_info"]["end"]) - $crash_profile["line_marker_info"]["start"]);

	$output_matches = array();
	preg_match("/<QADEBUG>kdumper\s+file\s+kdump.(\d+)\s+<BS>\s*.+\s*<\/BS><\/QADEBUG>/", $kdump_lines[0], $output_matches);

	if (count($output_matches) == 2) {
		$index = $output_matches[1];

		$variant_exec_id = -1;

		# Now we need to know what variant exec id this was created under.
		$rc = get_variant_exec_id_from_test_exec_id($error, $sql_handle, $crash_profile["line_marker_info"]["fk_test_exec_id"], $variant_exec_id);

		if ($rc == OK) {

			$crash_profile["kdump_elf_info"] = array();
			$rc = get_file_information_for_file_name_and_variant_id($error, $sql_handle, $crash_profile["kdump_elf_info"], $variant_exec_id, "kdump.".$index.".elf");

			if ($rc == OK) {
				$crash_profile["index_file"] = array();

				$rc = get_file_information_for_file_name_and_variant_id($error, $sql_handle, $crash_profile["index_file"], $variant_exec_id, "kdump",".".$index);
				if ($rc == OK) {

					$crash_profile["symbol_info"] = array();
					# Now get the attachment information for the symbol file.
					$rc = get_symbol_file_info_for_variant_exec_id($error, $sql_handle, $crash_profile["symbol_info"], $variant_exec_id);

					if ($rc == OK){
						# now we need to gzunzip everything first..
						if (gunzip($error, $crash_profile["kdump_elf_info"]["full_path"])) {
							$elf_file_name = $crash_profile["kdump_elf_info"]["attach_path"]."/".$crash_profile["kdump_elf_info"]["storage_rel_path"]."/".$crash_profile["kdump_elf_info"]["base_file_name"];

							if (gunzip($error, $crash_profile["symbol_info"]["full_path"])) {
								$symbol_file_name = $crash_profile["symbol_info"]["attach_path"]."/".$crash_profile["symbol_info"]["storage_rel_path"]."/".$crash_profile["symbol_info"]["base_file_name"].$crash_profile["symbol_info"]["src_ext"];


								$descriptorspec = array(
										   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
										   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
										   2 => array("pipe", "r") // stderr is a file to write to
										);

								$cwd = $crash_profile["kdump_elf_info"]["attach_path"]."/".$crash_profile["kdump_elf_info"]["storage_rel_path"];
								$env = array();

								$cmd = $qnx_tool_path."/nto".$_GET["arch"]."-gdb ".$symbol_file_name;

								$process = proc_open($cmd, $descriptorspec, $pipes, $cwd, $env);

								if (is_resource($process)) {
									// $pipes now looks like this:
									// 0 => writeable handle connected to child stdin
									// 1 => readable handle connected to child stdout
									// Any error output will be appended to /tmp/error-output.txt
									fwrite($pipes[0], "echo target remote | kdserver ".$elf_file_name."\\n\n");

									fwrite($pipes[0], "target remote | kdserver ".$elf_file_name."\n");

									fwrite($pipes[0], "echo [ian_is_totally_awesome_bt]\n");
									fwrite($pipes[0], "echo bt\\n\n");
									fwrite($pipes[0], "bt\n");
									fwrite($pipes[0], "echo [/ian_is_totally_awesome_bt]\n");
									fwrite($pipes[0], "echo [ian_is_totally_awesome_info_reg]\n");
									fwrite($pipes[0], "echo info reg\\n\n");
									fwrite($pipes[0], "info reg\n");
									fwrite($pipes[0], "echo [/ian_is_totally_awesome_info_reg]\n");
									fwrite($pipes[0], "echo [ian_is_totally_awesome_display]\n");
									fwrite($pipes[0], "echo display /100i \$pc-0d40\\n\n");
									fwrite($pipes[0], "display /100i \$pc-0d40\n");
									fwrite($pipes[0], "echo [/ian_is_totally_awesome_display]\n");
									fwrite($pipes[0], "quit\n");

									fwrite($pipes[0], "y\n");
									fclose($pipes[0]);

									$data = stream_get_contents($pipes[1]);

									fclose($pipes[1]);

									// It is important that you close any pipes before calling
									// proc_close in order to avoid a deadlock
									$return_value = proc_close($process);

									if ($return_value == 0) {
										if (count(trim($data)) > 0) {
											$pos = strrpos($data, "[/ian_is_totally_awesome_bt]");

											$bt_data = substr($data, 0, $pos);

											$pos = strpos($bt_data, "[ian_is_totally_awesome_bt]");

											$crash_profile["header"] =  trim($cmd."\n".substr($bt_data, 0,  $pos ));

											$crash_profile["back_trace"] = trim(substr($bt_data, $pos+strlen("[ian_is_totally_awesome_bt]"), strlen($bt_data)));

											$pos = strrpos($data, "[/ian_is_totally_awesome_info_reg]");

											$info_reg_data = substr($data, 0,  $pos);

											$pos = strpos($info_reg_data, "[ian_is_totally_awesome_info_reg]");

											$crash_profile["info_reg_data"] = trim(substr($info_reg_data, $pos + strlen("[ian_is_totally_awesome_info_reg]"), strlen($info_reg_data)));

											$pos = strrpos($data, "[/ian_is_totally_awesome_display]");

											$display = trim(substr($data, 0,  $pos));

											$pos = strpos($display, "[ian_is_totally_awesome_display]");

											$crash_profile["display"] = trim(substr($display, $pos + strlen("[ian_is_totally_awesome_display]"), strlen($display)));

											$keep_lines = array();
											$keep_lines[count($keep_lines)] = "                                -=Back Trace=-";

											$lines = explode("\n", $crash_profile["back_trace"]);

											// use this to shift off the first line
											array_shift ($lines);

											foreach($lines as $line) {
												$pos = strpos($line, "??");

												if ($pos !== FALSE){
													continue;
												}

												$pos = strpos($line, "(gdb)");

												if ($pos !== FALSE){

													$line = trim(substr($line, 5, strlen($line)));
												}

												if (strlen($line) <= 0) {
													continue;
												}

												$keep_lines[count($keep_lines)] = $line;
											}

											$lines = explode("\n", $crash_profile["display"]);



											$keep_lines[count($keep_lines)] = "                                -=Display=-";
											$next_break = False;
											$counter = 0;
											foreach($lines as $line) {
												$counter ++;

												if ($counter < 4){
													continue;
												}

												$line=trim($line);

												if (strlen($line) == 0){
													continue;
												}

												$pos = strpos($line, "=>");

												if ($pos !== FALSE){
													$pos = strpos($line, "<");
													if ($pos !== FALSE){
														$keep_lines[count($keep_lines)] = "=>".substr($line, $pos, strlen($line));
														# some times the info we want is on the next line.. so don't break right away.
														$next_break = True;
													}
												}
												else{
													$pos = strpos($line, "<");
													if ($pos === FALSE){
														$pos = 0;
													}
													$keep_lines[count($keep_lines)] = substr($line, $pos, strlen($line));

													if ($next_break){
														break;
													}
												}
											}
											$crash_profile["lines"] = $keep_lines;

											$crash_profile["regex"] = preg_quote(implode("\n",$crash_profile["lines"]));
											$crash_profile["regex"] = preg_replace("/[[:blank:]]+/", "\s*", $crash_profile["regex"]);


											$crash_profile["regex"] = preg_replace("/0x[a-fA-F0-9]+/", "0x[a-fA-F0-9]+", $crash_profile["regex"] );
											$crash_profile["regex"] = preg_replace("/=[0-9]+/", "=[0-9]+", $crash_profile["regex"]);
											$crash_profile["regex"] = preg_replace("/:[0-9]+/", ":[0-9]+", $crash_profile["regex"]);
											$crash_profile["regex"] = preg_replace("/\+[0-9]+/", "+[0-9]+", $crash_profile["regex"] );
										}
										else{
											$error = __FUNCTION__.":".__LINE__." GDB process returned no data.";
											$rc = ERROR_GENERAL;
										}
									}
									else{
										$error = __FUNCTION__.":".__LINE__." gdb process returned ".$return_value;
										$rc = ERROR_GENERAL;
									}
								}
								else{
									$rc = ERROR_GENERAL;
									$error = __FUNCTION__.":".__LINE__." Failed to regex out kdump index from line: ".$kdump_lines[0];
								}
								unlink($symbol_file_name );
							}
							unlink($elf_file_name);
						}
					}
				}
			}
		}
	}
	else {
		$rc = ERROR_GENERAL;
		$error = __FUNCTION__.":".__LINE__." Failed to regex out kdump index from line: ".$kdump_lines[0];
	}
	return $rc;
}

function generate_process_seg_crash_profile(&$error, $sql_handle, &$log_lines, &$crash_profile) {
	$rc = OK;
	$crash_profile["lines"] = array();
	$crash_profile["regex"] = array();

	$max_log_lines = count($log_lines);

	# Now scan back from the crash position to the first none empty line.
	for($scan_index = $crash_profile["line_marker_info"]["start"]-1; $scan_index > 0; $scan_index --){
		if (strlen($log_lines[$scan_index]) > 0) {
			break;
		}
	}

	$crash_profile["mod_start"] = $scan_index;

	# Now scan forward from the crash position to the first none empty line.
	for($scan_index = $crash_profile["line_marker_info"]["start"]+1; $scan_index < $max_log_lines; $scan_index ++) {
		if (strlen($log_lines[$scan_index]) > 0) {
			break;
		}
	}
		$crash_profile["mod_end"]  = $scan_index;

	$temp = array_splice($log_lines, $crash_profile["mod_start"] - key($log_lines), (($crash_profile["mod_end"]+1) - $crash_profile["mod_start"]));

	$counter = $crash_profile["mod_start"];
	$crash_profile["lines"] = array();

	foreach($temp as $line){
		if (strlen(trim($line)) > 0) {
			$crash_profile["lines"][$counter] = $line;
		}
		$counter++;
	}

	$crash_profile["regex"] = preg_quote(implode("\n",$crash_profile["lines"]));
	$crash_profile["regex"] = preg_replace("/\\\<TS\\\>.*\\\<\\/TS\\\>/", "\<TS\>.*\<\/TS\>", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/\\\<BS\\\>.*\\\<\\/BS\\\>/", "\<BS\>.*\<\/BS\>", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/Process \d{5,25}/", "Process \\d+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/pid \d{5,25}/", "pid \\d+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/code\\\=\d+/", "code\=\d+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/fltno\\\=\d+/", "fltno\=\d+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/ref\\\=[\da-f]+/", "ref\=[\da-f]+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/mapaddr\\\=[\da-f]+/", "mapaddr\=[\da-f]+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/ip\\\=[\da-f]+/", "ip\=[\da-f]+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/[\da-f]{16,16}/", "[\da-f]+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/\\:\d+/", ":\d+", $crash_profile["regex"]);
	$crash_profile["regex"] = preg_replace("/[[:blank:]]+/", "\s*", $crash_profile["regex"]);
	return $rc;
}

function get_line_marker_info_and_crash_profile(&$error, $sql_handle, $lm_id, &$crash_profile, $log_profile=NULL) {

	$rc = OK;

	# Get all the information we can from the lm_id we are passed.
	# The lm_id we are passed points to the crash line marker, not the test line marker.
	$crash_profile = array();
	$crash_profile["line_marker_info"] = array();

	$rc = get_info_for_line_marker_id($error, $sql_handle, 	$crash_profile["line_marker_info"], $lm_id);

	if ($rc == OK) {
		if ($log_profile == NULL){
			$log_profile=array();
			$rc = get_test_log_lines($error, $sql_handle, $_GET["test_exec_id"], $log_profile);
		}
	}

	if ($rc == OK) {

		if ($crash_profile["line_marker_info"]["line_marker_type"] == "process_seg") {
			$rc = generate_process_seg_crash_profile($error, $sql_handle, $log_profile["file_data"]["lines"], $crash_profile);
		}
		else if ($crash_profile["line_marker_info"]["line_marker_type"] == "kdump") {
			$rc =  generate_kdump_crash_profile($error, $sql_handle, $log_profile["file_data"]["lines"], $crash_profile);
		}
		else if ($crash_profile["line_marker_info"]["line_marker_type"] == "kernel_start") {
			echo "TODO: GET KERNEL START PROFILE";
		}
		else if ($crash_profile["line_marker_info"]["line_marker_type"] == "shutdown") {

			$crash_profile["lines"] = array();

			# Somtimes the shutdown message appears in the main log and sometimes it appears in the kdump log.
			# Check to see if the log attachment id and the shutdown attachment id are the same or differnt
			if ($log_profile["line_marker_info"]["fk_attachment_id"] == $crash_profile["line_marker_info"]["fk_attachment_id"]){

				# They are in the same file.
				$rc = generate_shutdown_crash_profile($error, $log_profile["lines"], $crash_profile,  $crash_profile["line_marker_info"]["start"], $crash_profile["line_marker_info"]["end"]);
			}
			else{
				$kdump_index_file_info = array();

				$rc = get_file_info_w_lines_for_attachment_id($error, $sql_handle, $kdump_index_file_info, $crash_profile["line_marker_info"]["fk_attachment_id"]);

				if ($rc == OK){

					$rc = generate_shutdown_crash_profile($error, $kdump_index_file_info["lines"], $crash_profile,  $crash_profile["line_marker_info"]["start"], $crash_profile["line_marker_info"]["end"]);
				}
			}
		}
		else{
			$rc = ERROR_GENERAL;
			$error = __FUNCTION__.":".__LINE__." Returned to many records:".$count;
		}
	}
	return $rc;
}


function get_test_log_lines(&$error, $sql_handle, $test_exec_id,  &$test_log_profile){

	$test_log_profile=array();
	$test_log_profile["line_marker_info"] = array();
	$test_log_profile["file_data"] = array();
	$rc = get_line_marker_info_for_type($error, $sql_handle, $test_log_profile["line_marker_info"], $test_exec_id , "full_test");

	if ($rc == OK) {
		# Get the log lines, note that \r \n will be removed from these lines automatically.
		$rc = get_file_info_w_lines_for_attachment_id($error, $sql_handle, $test_log_profile["file_data"],
													  $test_log_profile["line_marker_info"]["fk_attachment_id"],
													  $test_log_profile["line_marker_info"]["start"], $test_log_profile["line_marker_info"]["end"]);
	}
	return $rc;
}


# Pass the function the lm_id of the crash that we want to look at..
# from it we can determine the full test log that has has the same test_id.
function get_log_and_crash_profile(&$error, $sql_handle, $lm_id, &$test_profile){
	# Start out by getting the test log.
	# To get the test log we need to find the line_marker with a type set to test full
	# for the passed test_exec_id.

	$test_profile = array();
	$test_profile["log"] = array();
	$test_profile["crash"] = array();

	$rc = get_test_log_lines($error, $sql_handle, $_GET["test_exec_id"], $test_profile["log"]);

	if ($rc == OK) {
		$rc = get_line_marker_info_and_crash_profile($error, $sql_handle, $lm_id, $test_profile["crash"]);
	}

	return $rc;
}

function check_regex($regex_profile, $crash_profile, &$error){
	$delimiter_list = array('`','!', '@', '#', '$', '%', '^', '&', ',', '\'', ':', '/');
	$delimiter = NULL;

	$regex_profile = str_replace("\r", "", $regex_profile);
	$regex_profile = str_replace("\n", "", $regex_profile);

	$crash_profile = str_replace("\r", "", $crash_profile);
	$crash_profile = str_replace("\n", "", $crash_profile);

	foreach($delimiter_list as $test) {
		$pos = strpos($regex_profile, $test);

		if ($pos === FALSE){
			$delimiter = $test;
			break;
		}
	}

	if ($delimiter == NULL){
		$error = "No delimiter could be found!";
		return False;
	}

	$result = preg_match($delimiter.$regex_profile.$delimiter, $crash_profile, $output);

	if ($result != 1) {
		$error =  "Error: regex does not match crash profile.";
		return False;
	}
	return True;
}

function get_known_crash_info($sql_handle){
	global $reporter_enum, $bug_reporter_unique_ref;
	$rc = OK;
	$rows = array();

	$tables = array("crash_known");

	$where = array( "crash_known.crash_known_id"=>$_GET["crash_known_id"]);

	$select = array("type_enum", "fk_project_bug_id","UNCOMPRESS(regex) as regex");

	$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

	if ($rc == OK){
		$regex_profile = $rows[0]["regex"];
		$type_enum = $rows[0]["type_enum"];
		if (strlen($rows[0]["fk_project_bug_id"]) > 0){

			$tables = array("project_bug","bug_root");
			$where = array( "project_bug_id"=>$rows[0]["fk_project_bug_id"],
							"project_bug.fk_bug_root_id"=>"bug_root.bug_root_id"
						  );
			$select = array("recorder_enum", "unique_ref");

			$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

			if ($rc== OK){
				$reporter_enum = $rows[0]["recorder_enum"];
				$bug_reporter_unique_ref = $rows[0]["unique_ref"];
			}
		}
	}

	return $rc;
}

gen_footer();
?>

