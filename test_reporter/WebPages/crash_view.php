<?php
include_once("assist.php");
include_once("help_log_display.php");
include_once("db_helper.php");

gen_head("Crash View", "style.css");
$error = NULL;

if (isset($_GET["reporter_type"]) == FALSE){
	$_GET["reporter_type"] = "ji";
}

$expected_get_keys = array( "project", "exec", "lm_id", "attach_id", "start", "end", "test_exec_id", "lm_type", "lm_type_id", "sub_type", "sub_type_id", "target", "arch", "variant", "suite", "exec_path", "test_name", "params", "result", "test_suite_root_id", "test_root_id", "crash_known_id");

$ok = True;
foreach($expected_get_keys as $key){

	if (isset($_GET[$key]) == False){
		$ok = False;
		echo $key." is missing from the URL";
	}
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


if ($ok) {

	$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

	if ($sql_handle != NULL) {

		$rows = array();
		echo get_master_core($error, $sql_handle, $rows, "test_revision.fk_test_root_id=".$_GET["test_root_id"]);

		echo "<BR>".$error."<BR>";

		# Get the "Full test" line type id
		$query = 'SELECT line_marker_type_id from line_marker_type WHERE name="full_test"';

		$full_test_result = sql_query($sql_handle, $query, $error);

		if ($full_test_result) {
			$full_test_rows = $full_test_result->fetchall();
			$full_test_id = $full_test_rows[0]["line_marker_type_id"];

			# Lets get the log output for this test.
			$query = 'SELECT fk_attachment_id, start, end FROM line_marker WHERE fk_test_exec_id='.$_GET["test_exec_id"].' and fk_line_marker_type_id='.$full_test_id;

			$full_test_log_result = sql_query($sql_handle, $query, $error);

			if ($full_test_log_result){

				$rows = $full_test_log_result->fetchall();

				$test_log_lines = get_text_line_array_for_line_marker($sql_handle, $rows[0]["fk_attachment_id"], $rows[0]["start"], $rows[0]["end"], $error );

				// strip the log lines of new lines
				foreach($test_log_lines as &$lines) {
					$lines = str_replace("\n", "", $lines);
					$lines = str_replace("\r", "", $lines);
				}

				if ($_GET["end"] > $rows[0]["end"]){
					$_GET["end"] = $rows[0]["end"];
				}

				$show_rows = min(count($test_log_lines), 35);

				echo '<center><textarea name="test_log" cols="200" rows="'.$show_rows.'">';

				$index =  $rows[0]["start"];
				foreach($test_log_lines as $line){

					if (($index >=  $_GET["start"])  and ($index <=  $_GET["end"]))  {
						echo $index.") =>".$line."\n";
					}
					else{
						echo $index.") ".$line."\n";
					}
					$index  = $index  + 1;
				}
				echo "</textarea></center>";

				$max_log_lines = count($test_log_lines);

				# check to see what type of crash this is and then process it accordingly.
				if ($_GET["lm_type"] == "process_seg"){
					// The fist display line will be at index 0, but the relative database line is at $rows[0]["start"];
					$relative_offset_converion = $rows[0]["start"];

					if (isset($_GET["New"]) === False){
						# Now scan back from the crash position to the first none empty line.
						for($scan_index = ($_GET["start"] - $relative_offset_converion)-1; $scan_index > 0; $scan_index --){

							if (strlen($test_log_lines[$scan_index]) > 0) {
								break;
							}
						}

						$_GET["start"] = $relative_offset_converion + $scan_index;

						# Now scan forward from the crash position to the first none empty line.
						for($scan_index = ($_GET["end"] - $relative_offset_converion)+1; $scan_index < $max_log_lines; $scan_index ++) {
							if (strlen($test_log_lines[$scan_index]) > 0) {
								break;
							}
						}

						$_GET["end"] = $relative_offset_converion + $scan_index;
					}

					$temp_lines =  array_splice($test_log_lines,  ($_GET["start"]-$relative_offset_converion),  (($_GET["end"]-$relative_offset_converion)+1) - ($_GET["start"] - $relative_offset_converion));
					$crash_pro_file_lines = array();
					# remove any white space from the crash profile.
					foreach($temp_lines as &$temp_line){
						$temp_line = trim($temp_line);
						if (strlen($temp_line)>0){
							$crash_pro_file_lines[count($crash_pro_file_lines)]=$temp_line;
						}
					}

					$show_rows = min(count($crash_pro_file_lines), 10);

					$crash_profile = implode("\n",$crash_pro_file_lines);

					echo "<center>Crash Profile</center>";
					echo '<center><textarea cols="200" rows="'.$show_rows.'">';
					echo $crash_profile;
					echo "</textarea></center>";

					if (isset($_GET["regex_profile"]) == FALSE) {

						$regex_profile = preg_quote($crash_profile);
						$regex_profile = preg_replace("/\\\<TS\\\>.*\\\<\\/TS\\\>/", "\<TS\>.*\<\/TS\>", $regex_profile);
						$regex_profile = preg_replace("/\\\<BS\\\>.*\\\<\\/BS\\\>/", "\<BS\>.*\<\/BS\>", $regex_profile);
						$regex_profile = preg_replace("/Process \d{5,25}/", "Process \\d+", $regex_profile);
						$regex_profile = preg_replace("/pid \d{5,25}/", "pid \\d+", $regex_profile);
						$regex_profile = preg_replace("/code\\\=\d+/", "code\=\d+", $regex_profile);
						$regex_profile = preg_replace("/fltno\\\=\d+/", "fltno\=\d+", $regex_profile);
						$regex_profile = preg_replace("/ref\\\=[\da-f]+/", "ref\=[\da-f]+", $regex_profile);
						$regex_profile = preg_replace("/mapaddr\\\=[\da-f]+/", "mapaddr\=[\da-f]+", $regex_profile);
						$regex_profile = preg_replace("/ip\\\=[\da-f]+/", "ip\=[\da-f]+", $regex_profile);
						$regex_profile = preg_replace("/[\da-f]{16,16}/", "[\da-f]+", $regex_profile);
						$regex_profile = preg_replace("/\\:\d+/", ":\d+", $regex_profile);
						$regex_profile = preg_replace("/[[:blank:]]+/", "\s*", $regex_profile);
					}
					else{
						$regex_profile = $_GET["regex_profile"];
					}


					# Query the database and see if we have any known crash dumps for this test already

					echo "TODO-- PUT KNOWN CRASH HERE!!!<BR>";

					echo '<form>';

					foreach(array_keys($_GET) as $key){
							echo '<input type=hidden name="'.$key.'" value="'.$_GET[$key].'" >';
					}
					echo "<center>New Regex Profile</center>";
					echo '<center><textarea name="regex_profile" cols="200" rows="'.$show_rows.'">';
					echo $regex_profile;
					echo "</textarea></center>";

					$status_types = array("error", "generated");

					echo '<label>Crash orgin: </label><select name="status">';
					foreach($status_types as $status_type){
						if ($status_type == $_GET["status"]){
							echo '<option value="'.$status_type.'" selected>'.$status_type."</option>";
						}
						else{
							echo '<option value="'.$status_type.'" >'.$status_type."</option>";
						}
					}
					echo '</select><BR>';

					$reporter_types = array("pr", "ji");

					echo '<label>Reporter Type: </label><select name="reporter">';
					foreach($reporter_types as $reporter_type){
						if ($reporter_type == $_GET["reporter_type"]){
							echo '<option value="'.$reporter_type.'" selected>'.$reporter_type."</option>";
						}
						else{
							echo '<option value="'.$reporter_type.'" >'.$reporter_type."</option>";
						}
					}
					echo '</select><BR>';
					if (isset($_GET["bug_reporter_unique_ref"])) {
						echo '<input type=text name="bug_reporter_unique_ref" value="'.$_GET["bug_reporter_unique_ref"].'" >';
					}
					else{
						echo '<input type=text name="bug_reporter_unique_ref">';
					}

					echo '<center><input type="submit" name="New" value="New" ></center>';
					echo '</form>';
				}

				if (isset($_GET["New"])) {
					echo "<HR>";

					# check to see what type of crash this is and then process it accordingly.
					if ($_GET["type"] == "process_seg") {

						# first check to make sure the regex matches the profile.
						$regex_profile = $_GET["regex_profile"];

						if (check_regex($regex_profile, $crash_profile, $error)){

							$OK = True;

							# check to see if the user selected generated or error.
							if ($_GET["status"] == "error") {
								if (isset($_GET["bug_reporter_unique_ref"])){
									if (strlen($_GET["bug_reporter_unique_ref"]) <= 0){
										echo "Error: Bug reporter unique id missing.";
										$OK = False;
									}
								}
								else{
									echo "Error: Crash orgin (error) mode selected but no bug id was provided.";
									$OK=False;
								}
							}

							if ($OK) {

								$type = $_GET["type"];

								if ($_GET["type"] == "process_seg") {
									$type = $_GET["sub"];
								}
								echo "Type: ".$type."<BR>";
								echo "Status: ".$_GET["status"]."<BR>";
								echo "Reporter: ".$_GET["reporter"]."<BR>";

								if (isset($_GET["bug_reporter_unique_ref"])){
									echo "Unique Bug ID: ".$_GET["bug_reporter_unique_ref"]."<BR>";
								}
								else{
									echo "Unique Bug ID: Not Set <BR>";
									$_GET["bug_reporter_unique_ref"] = NULL;
								}

								echo "Test_suite_id: ".$_GET["test_suite_root_id"]."<BR>";
								echo "test_root_id: ".$_GET["test_root_id"]."<BR>";

								$crash_type_id = NULL;
								$crash_known_id = NULL;
								$reporter_id   = NULL;
								$project_bug_id  = NULL;

								# Start off by getting the crash type id
								$rows = array();

								$crash_type_id = get_crash_type_id($error, $sql_handle, $_GET["project"], $type);

								if ($crash_type_id > 0) {

									if ($_GET["bug_reporter_unique_ref"] != NULL) {
										$project_bug_id = add_project_bug($error, $sql_handle, $_GET["reporter"], $_GET["bug_reporter_unique_ref"], $_GET["project"]);
									}

									# Checkk to see if this regex profile already exists.
									if ($project_bug_id == NULL) {
										$query = 'SELECT crash_known_id FROM crash_known WHERE fk_crash_type_id='.$crash_type_id.' and fk_test_root_id='.$_GET["test_root_id"].' and fk_test_suite_root_id='.$_GET["test_suite_root_id"].' and type_enum="'.$_GET["status"].'" and UNCOMPRESS(regex)="'.addslashes($regex_profile).'"';
									}
									else {
										$query = 'SELECT crash_known_id FROM crash_known WHERE fk_project_bug_id='.$project_bug_id.' and fk_crash_type_id='.$crash_type_id.' and fk_test_root_id='.$_GET["test_root_id"].' and fk_test_suite_root_id='.$_GET["test_suite_root_id"].' and type_enum="'.$_GET["status"].'" and UNCOMPRESS(regex)="'.addslashes($regex_profile).'"';
									}

									$regex_query_result = $bug_result = sql_query($sql_handle, $query, $error);

									if ($regex_query_result) {

										$rows = $regex_query_result->fetchall();

										if (count($rows) == 0) {

											if ($project_bug_id == NULL) {
												$query = 'INSERT INTO crash_known (fk_crash_type_id, fk_test_root_id, fk_test_suite_root_id, type_enum, regex, created) VALUES ('.$crash_type_id.', '.$_GET["test_root_id"].', '.$_GET["test_suite_root_id"].',"'.$_GET["status"].'", COMPRESS("'.addslashes($regex_profile).'"), NOW())';
											}
											else{
												$query = 'INSERT INTO crash_known (fk_project_bug_id, fk_crash_type_id, fk_test_root_id, fk_test_suite_root_id, type_enum, regex, created) VALUES ('.$project_bug_id.','.$crash_type_id.', '.$_GET["test_root_id"].', '.$_GET["test_suite_root_id"].',"'.$_GET["status"].'", COMPRESS("'.addslashes($regex_profile).'"), NOW())';
											}

											$insert_result = sql_query($sql_handle, $query, $error);

											if ($insert_result){
												$crash_known_id = $sql_handle->lastInsertId();
												echo "ID:".$crash_known_id."<BR>";
											}
											else{

												echo $query."<BR>".$error;
												$OK=False;
											}
										}
										else{
											echo "Regex already exists in the database.";
											$crash_known_id =  $rows[0]["crash_known_id"];
										}


										if ($OK) {
											# Now update the the crash exec for this guy..
											$query = 'UPDATE crash_exec SET fk_crash_known_id='.$crash_known_id.' WHERE fk_line_marker_id='.$_GET["lm"];

											$result = sql_query($sql_handle, $query, $error);

											if ($result){

												/*
													Now look for other instances of this test (test_root_id) within this child project.. That have a crash that has a known crash id of NULL.
													And compare them to this regex.
												*/

												$query = 'SELECT * FROM crash_exec, line_marker WHERE ';




											}
											else{
												echo $query."<BR>".$error."<BR>";
											}

										}
									}
									else{
										echo $query."<BR>".$error;
										$OK=False;
									}
								}
								else{
									echo $error;
									$OK = False;
								}
							}
						}
						else{
							echo "<center>".$error."</center>";
						}
					}
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
	else{
		echo $error;

	}
}

gen_footer();
?>

