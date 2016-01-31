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

gen_head("Proj: ".$_GET["project"]."Reg: ".$_GET["exec"]." LM: ".$_GET["lm_id"], "style.css");

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
				show(implode("\n", $test_profile["crash"]["header"]),"GDB Header", $line_count, 140, TRUE);
			}

			if (array_key_exists("back_trace", $test_profile["crash"])){
				show(implode("\n", $test_profile["crash"]["back_trace"]),"GDB Header", $line_count, 140, TRUE);
			}

			if (array_key_exists("back_trace", $test_profile["crash"])){
				show(implode("\n", $test_profile["crash"]["back_trace"]),"Back Trace", $line_count, 140, TRUE);
			}
			
			if (array_key_exists("info_reg_data", $test_profile["crash"])){
				show(implode("\n", $test_profile["crash"]["info_reg_data"]),"Back Trace", $line_count, 140, TRUE);
			}
			
			if (array_key_exists("display", $test_profile["crash"])){
				show(implode("\n", $test_profile["crash"]["display"]),"Back Trace", $line_count, 140, TRUE);
			}

			$line_count = min(count($test_profile["crash"]["lines"]), 10);

			$crash_profile_lines = implode("\n", $test_profile["crash"]["lines"]);

			show($crash_profile_lines,"Crash Profile", $line_count, 140, TRUE);


			/*
				Regex box control variables
			*/
			$readonly = False;
			$crash_known_id = array();
			$regex = array();
			$type_enum = array();
			$reporter_enum = array();
			$bug_reporter_unique_ref=array();

			$crash_known_id[0] = $_GET["crash_known_id"];


			$regex_index = 0;
			/*	
				End of control variables.
			*/

			if (isset($_GET["regex"])){
				$regex[0] = $_GET["regex"];
				$type_enum[0] = $_GET["type_enum"];
				$reporter_enum[0] =  $_GET["reporter_enum"];
				$bug_reporter_unique_ref[0] = $_GET["unique_ref"];
			}
			else {
				if (intval($_GET["crash_known_id"])> 0) {

					$rows = array();
					$where = array(	"crash_known_id"=> $_GET["crash_known_id"]);

					$rc = get_crash_known_with_bug_info($error, $sql_handle, $rows, $where);

					show($rows);
					
					if ($rc == OK) {


						$regex[0] = $rows[0]["regex"];
						$type_enum[0] = $rows[0]["type_enum"];
						$reporter_enum[0] = $rows[0]["recorder_enum"];
						$bug_reporter_unique_ref[0] = $rows[0]["unique_ref"];
					}
				}
				else{
					$regex[0] = $test_profile["crash"]["regex"];
				}
			}

	
			$type = $_GET["lm_type"];

			if ($_GET["lm_type"] == "process_seg") {
				$type = $_GET["sub_type"];
			}

			$crash_type_id = get_crash_type_id($error, $sql_handle, $_GET["project"], $type);

			if ($crash_type_id > 0) {

				/* Query the database and see if there are any other crash regex of this type for this test */
				$rows = array();
				$where = array("fk_crash_type_id"=> intval($crash_type_id),
							   "fk_test_root_id" => intval($_GET["test_root_id"]));
				
				$where_string = NULL;

				if (intval($_GET["crash_known_id"])> 0) {
					$where_string ="crash_known_id!=".$_GET["crash_known_id"];
				}

				$rc = get_crash_known_with_bug_info($error, $sql_handle, $rows, $where, $where_string);

				if ($rc == OK)
				{
					foreach($rows as $row){
						$regex[count($regex)] = $row["regex"];
						$crash_known_id[count($crash_known_id)] =  $row["crash_known_id"];
						$type_enum[count($type_enum)] = $row["type_enum"];
						$reporter_enum[count($reporter_enum)] = $row["recorder_enum"];
						$bug_reporter_unique_ref[count($bug_reporter_unique_ref)] = $row["unique_ref"];
					}
				}
			}
			else{
				$rc = $crash_type_id;
			}


			if ($rc == OK) {
				
				$max_regex_index = count($regex);
				if (isset($_GET["regex_index"])){
					if ($_GET["regex_index"] < $max_regex_index){
						$regex_index = $_GET["regex_index"];
					}
				}

				if ($regex_index > 0) {
					$readonly = True;
				}

				echo '<form>';
				dup_get_input_for_form(array("crash_known_id"));

				echo '<input type="hidden" name="known_crash_id" value='.$crash_known_id[$regex_index].' >';
				echo '<input type="hidden" name="regex_index" value='.$regex_index.' >';				

				echo "<center><strong>Regex Profile (".($regex_index+1)." of ".$max_regex_index.")</strong></center>";
			
				echo '<table align="center" width=50%>';
				echo '<tr>';

				echo '<td align="center" >';
				$type_enums = array("error", "generated");
				
				echo '<label>Crash Type: <label><select name="type_enum">';			
				foreach($type_enums as $value){
					if ($value == $type_enum[$regex_index]){
						echo '<option value="'.$value.'" selected>'.$value."</option>";
					}
					else{
						echo '<option value="'.$value.'" >'.$value."</option>";
					}
				}
				echo '</select>';
				echo '</td>';

				$recorder_enums = array("pr", "ji");

				echo '<td align="center" >';
				echo '<label>Reporter Type: <label><select name="reporter_enum">';
				foreach($recorder_enums as $value){
					if ($value == $reporter_enum[$regex_index]){
						echo '<option value="'.$value.'" selected>'.$value."</option>";
					}
					else{
						echo '<option value="'.$value.'" >'.$value."</option>";
					}
				}
				echo '</select>';
				echo '</td >';

				echo '<td align="center" >';
				if ($bug_reporter_unique_ref != NULL) {
					echo '<label>Unique Ref: </label><input type=text name="bug_reporter_unique_ref" value="'.$bug_reporter_unique_ref[$regex_index].'" >';
				}
				else{
					echo '<label>Unique Ref: </label><input type=text name="bug_reporter_unique_ref">';
				}
				echo '</td>';
				echo '</tr>';
				echo '</table>';

				if ($readonly){
					echo '<center><textarea name="regex" cols=140 rows='.$line_count.' readonly>';
				}
				else {
					echo '<center><textarea name="regex" cols=140 rows='.$line_count.' >';
				}

				echo $regex[$regex_index];
				
				echo '</textarea></center>';

				echo '<table align="center" width="20%">';
				echo '<tr>';
				
				echo '<td align="center">';
				echo '<input type="submit" name="submit" value="Test Change" >';
				echo '</td>';
				
			

				if (check_regex($regex[$regex_index], $crash_profile_lines, $error)) {
					echo '<td align="center">';
					echo "Match";
					echo '</td>';


					if (intval($_GET["crash_known_id"])> 0) {
						echo '<td align="center">';
						echo '<input type="submit" name="submit" value="Update" >';
						echo '</td>';
					}
					else {			
						echo '<td align="center">';
						echo '<input type="submit" name="submit" value="Apply" >';
						echo '</td>';
					}						
				}
				else{
					echo '<td>';				
					echo "No Match";
					echo '</td>';

					echo '<td align="center">';
					echo '&nbsp';
					echo '</td>';								
				}


				echo '</tr>';

				echo '</table>';
				echo '</form>';
			}
			else{
				echo $error;
			}
		}
		else{
			echo $error;
		}
	}
	else{
		echo $error;
	}
}

function generate_shutdown_crash_profile(&$error, &$log_lines, &$crash_profile, $start, &$end){
	$rc = OK;
	$crash_profile["lines"] = array();
	$crash_profile["regex"] = array();
	$max_lines = count($log_lines);


	$crash_profile["lines"][$start] = $log_lines[$start];

	for($index =  $start+1; $index < $max_lines; $index ++) {
		$pos = strpos($log_lines[$index],'$URL');

		if ($pos !== FALSE){
			if ($pos == 0){
				$crash_profile["lines"][$index] = $log_lines[$index];
				break;
			}
		}
	}

	if ($rc == OK){
		$crash_profile["regex"] = preg_quote(implode("\n",$crash_profile["lines"]));
		$crash_profile["regex"] = preg_replace("/[[:blank:]]+/", "\s*", $crash_profile["regex"]);		
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


											$lines = explode("\n", $crash_profile["display"]);


											$keep_lines = array();

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

