<?php
ini_set ( 'max_execution_time', 1200);
include_once("assist.php");
include_once("help_log_display.php");
include_once("db_helper.php");

gen_head("Expectations", "style.css");
$error = NULL;
define("DEF_EXPECTED_NOT_FOUND", -3);
define("DEF_FOUND_BUT_EXEC_TIME_MISMATCH", -2);
define("DEF_FOUND_RESULT_NO_MATCH", -1);
define("DEF_NOT_FOUND", 0);
define("DEF_FOUND", 1);
define("DEF_FOUND_FUTURE_DATE", 2);


function get_expected_results(&$error, &$sql_handle, &$expected_rows, $exec_type_id, $variant_root_id, $date){
	$expected_rows = array();
	$tables = array("test_expected","variant_root", "target");

	$where = array("test_expected.fk_variant_root_id"=>"variant_root.variant_root_id",
				   "variant_root.fk_target_id"=>"target.target_id",
				   "target.fk_project_child_id"=> $_GET["project"],
				   "fk_exec_type_id"=>$exec_type_id,
				   "variant_root_id"=>$variant_root_id);


	//$extra_where = "\"".$date."\" BETWEEN start_date AND end_date";

	$extra_where = "\"".$date."\" <= end_date";

	$select = array("test_expected_id", "fk_test_revision_id", "fk_test_suite_root_id", "exec_time_secs", "fk_result_tag_id", "start_date", "end_date");

	$rc = select($error, $sql_handle, $expected_rows, $tables, $select, $where, $extra_where);

	if ($rc == OK) {

		foreach($expected_rows as &$row){
			$row["check"] = DEF_EXPECTED_NOT_FOUND;
		}
		return True;
	}
	else{
		echo  "Error: ".$error."<BR>";
		return False;
	}
}

if (isset($_GET["project"])) {
	if (isset($_GET["exec"])) {
		$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

		if ($sql_handle != NULL) {

			$rows = array();
			$tables = array("exec");
			$where = array( "exec_id"=>$_GET["exec"]);
			$select = array("fk_exec_type_id", "created");

			$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

			if ($rc == OK){
				if (count($rows) == 1){
					$exec_type_id = $rows[0]["fk_exec_type_id"];
					$exec_date = $rows[0]["created"];

					$exec_date_one_second_later = date ("Y-m-d H:i:s",strtotime($exec_date)+1);


					# Get all the test results for this exec
					$tables = array("test_exec", "variant_exec", "test_suite_root", "test_revision", "test_root", "variant_root", "arch", "target");
					$where = array("test_exec.fk_variant_exec_id"=>"variant_exec.variant_exec_id",
								   "variant_exec.fk_exec_id"=>$_GET["exec"],
								   "test_exec.fk_test_suite_root_id" => "test_suite_root.test_suite_root_id",
								   "test_exec.fk_test_revision_id"=>"test_revision.test_revision_id",
								   "test_revision.fk_test_root_id"=>"test_root.test_root_id",
								   "variant_exec.fk_variant_root_id"=>"variant_root.variant_root_id",
								   "variant_root.fk_target_id"=>"target.target_id",
								   "variant_root.fk_arch_id"=>"arch.arch_id");


					$select = array("test_exec_id", "target.name as target", "arch.name as arch", "variant_root.variant", "fk_test_suite_root_id","test_root.exec_path", "test_root.name", "test_root.params","test_suite_root.name as suite_name", "test_revision.unique_ref" ,"fk_test_revision_id", "fk_result_tag_id", "fk_variant_root_id", "test_exec.exec_time_secs");

					$rc = select($error, $sql_handle, $rows, $tables, $select, $where, NULL, NULL, "fk_variant_root_id ASC, fk_test_suite_root_id ASC, fk_test_revision_id ASC");

					if ($rc == OK) {
						$missing_expected = array();

						$expected_rows = NULL;

						$current_variant_id = 0;
						$found_type = DEF_NOT_FOUND;

						if (isset($_GET["test_submit"])){
							$keys = array_keys($_GET);

							$row_start_index = 0;
							$max_rows = count($rows);

							foreach($keys as $key){
								if (strlen($key) >= 3) {
									if ($key[1] == '_') {

										$action = $key[0];
										$test_exec_id = intval(substr($key, 2, strlen($key)));
										$radio_setting = $_GET[$key];

										for($index=$row_start_index; $index < $max_rows; $index++) {
											if ($rows[$index]["exec_time_secs"]==NULL) {
												$rows[$index]["exec_time_secs"] = 0;
											}

											if ($rows[$index]["test_exec_id"] == $test_exec_id) {

												if ($action == 'a') {
													$insert_dict = array("fk_variant_root_id"=>$rows[$index]["fk_variant_root_id"],
																		 "fk_test_suite_root_id"=>$rows[$index]["fk_test_suite_root_id"],
																		 "fk_test_revision_id"=>$rows[$index]["fk_test_revision_id"],
																		 "fk_exec_type_id"=>$exec_type_id,
																		 "fk_result_tag_id"=>$rows[$index]["fk_result_tag_id"],
																		 "exec_time_secs"=>$rows[$index]["exec_time_secs"],
																		 "end_date"=>"2999-12-31 23:59:59",
																		 "created"=>"now()"
																		);

													if ($radio_setting == 't') {
														$insert_dict["start_date"] = $exec_date;
													}
													elseif ($radio_setting == 'a') {
														$insert_dict["start_date"] = $exec_date_one_second_later;
													}
													elseif ($radio_setting == '.') {
														continue;
													}
													else{
														die("Error: Unknown Add radio setting action :".$radio_setting);
													}

													$rc = insert($error, $sql_handle, "test_expected", $insert_dict, True);

													if ($rc <= 0){
														if ($rc != ERROR_VALUE_EXISTS){
															die($error);
														}
														else{
															$error = NULL;
														}
													}
												}
												else{
													die("Error: Unknown managed action :".$action);
												}

												echo $action." ".$test_exec_id." ".$radio_setting."<BR>";
												$row_start_index = $index + 1;
												break;
											}
										}
									}
								}
							}
						}
						flush();

						foreach($rows as &$row) {
							$row["status"] = DEF_NOT_FOUND;

							if ($row["exec_time_secs"]==NULL) {
								$row["exec_time_secs"] = 0;
							}

							if ($row["fk_variant_root_id"] != $current_variant_id){

								if ($expected_rows != NULL) {
									foreach($expected_rows as $expected_row){
										if ($expected_row["check"] == DEF_EXPECTED_NOT_FOUND){
											$missing_expected[count($missing_expected)] = $expected_row;
										}
									}
								}

								if (get_expected_results($error, $sql_handle, $expected_rows, $exec_type_id ,$row["fk_variant_root_id"], $exec_date )){
									$current_variant_id = $row["fk_variant_root_id"];
								}
								else{
									echo "Error: ".$error;
									break;
								}
							}

							foreach($expected_rows as &$expected_row) {
								if ($expected_row["fk_test_suite_root_id"] == $row["fk_test_suite_root_id"]) {
									if ($expected_row["fk_test_revision_id"] == $row["fk_test_revision_id"]) {
										if (strtotime($exec_date) >= strtotime($expected_row["start_date"])) {
											if($expected_row["fk_result_tag_id"] == $row["fk_result_tag_id"]) {

												if ($expected_row["exec_time_secs"] > 0){
													$min_threshold = $expected_row["exec_time_secs"] - ($expected_row["exec_time_secs"] * 0.02);
													$max_threshold = $expected_row["exec_time_secs"] + ($expected_row["exec_time_secs"] * 0.02);
												}
												else{
													$min_threshold = 0;
													$max_threshold = 1;
												}

												if (($row["exec_time_secs"] >= $min_threshold) and ($row["exec_time_secs"] <= $max_threshold)) {
													$expected_row["check"] = DEF_FOUND;
													$row["status"]  = DEF_FOUND;
												}
												else {
													$expected_row["check"] = DEF_FOUND_BUT_EXEC_TIME_MISMATCH;
													$row["status"]  = DEF_FOUND_BUT_EXEC_TIME_MISMATCH;
													$row["execpted"] = $expected_row;
												}
											}
											else{
												$expected_row["check"] = DEF_FOUND_RESULT_NO_MATCH;
												$row["status"] = DEF_FOUND_RESULT_NO_MATCH;
												$row["execpted"] = $expected_row;
											}
										}
										else{
											$expected_row["check"] = DEF_FOUND_FUTURE_DATE;
											$row["status"] = DEF_FOUND_FUTURE_DATE;
											$row["execpted"] = $expected_row;
										}
									}
								}
							} // end of for foreach($expected_rows as &$expected_row)
						} // end of foreach($rows as &$row) {

						show($rows, "Test Exec Rows");

						show($missing_expected, "Missing Expected");


						echo '<form>';

						echo '<input type=hidden name="project" value="'.$_GET["project"].'" >';
						echo '<input type=hidden name="exec" value="'.$_GET["exec"].'" >';

						echo '<table align="center" border="2" >';
						echo '<tr>';

						echo '<th>';
						echo "Target";
						echo '</th>';

						echo '<th>';
						echo "Arch";
						echo '</th>';

						echo '<th>';
						echo "Variant";
						echo '</th>';

						echo '<th>';
						echo "Test Suite";
						echo '</th>';

						echo '<th>';
						echo "Path";
						echo '</th>';

						echo '<th>';
						echo "Name";
						echo '</th>';

						echo '<th>';
						echo "Parameters";
						echo '</th>';

						echo '<th>';
						echo "Status";
						echo '</th>';

						echo '<th>';
						echo "Choices";
						echo '</th>';


						echo '</tr>';
						foreach($rows as $row) {

							if ($row["status"] == DEF_FOUND){
								continue;
							}

							echo '<tr>';
							echo '<td>';
							echo $row["target"];
							echo '</td>';

							echo '<td>';
							echo $row["arch"];
							echo '</td>';

							echo '<td>';
							echo $row["variant"];
							echo '</td>';

							echo '<td>';
							echo $row["suite_name"];
							echo '</td>';

							echo '<td>';
							echo $row["exec_path"];
							echo '</td>';

							echo '<td>';
							echo $row["name"];
							echo '</td>';

							echo '<td>';
							echo $row["params"];
							echo '</td>';

							echo '<td>';
							if ($row["status"] == DEF_NOT_FOUND) {
								echo "Not Found";
							}
							else if ($row["status"] == DEF_FOUND_RESULT_NO_MATCH) {
								echo "Result Mismatch";
							}
							else if ($row["status"] == DEF_FOUND_BUT_EXEC_TIME_MISMATCH) {
								echo "Exec Time Mismatch";
							}
							echo '</td>';


							echo '<td>';

							if ($row["status"] == DEF_NOT_FOUND) {
								echo '<input type="radio" name="a_'.$row["test_exec_id"].'" value="." /><label>Do not Add</label><BR>';
								echo '<input type="radio" name="a_'.$row["test_exec_id"].'" value="t" ><label>Add  ('.$exec_date.')</label><BR>';
								echo '<input type="radio" name="a_'.$row["test_exec_id"].'" value="a" ><label>Add After ('.$exec_date_one_second_later.')</label><BR>';
							}
							else if ($row["status"] == DEF_FOUND_RESULT_NO_MATCH) {
								echo "Result Mismatch";
							}
							else if ($row["status"] == DEF_FOUND_BUT_EXEC_TIME_MISMATCH) {
								echo "Exec Time Mismatch";
							}
							else if ($row["status"] == DEF_FOUND_FUTURE_DATE) {
								echo "Future Match:".$row["execpted"]["start_date"];
							}

							echo '</td>';


							echo '</tr>';
						}

						echo '</table>';
						echo '<center><input type="submit" name="test_submit" value="submit"></center>';
						echo "</form>";



					}
					else {
						echo "Error: ".$error."<BR>";
					}
				}
				else{
					echo "Error: Expected a row count of 1 and instead got ".count($row)."<BR>";
				}
			}
			else{
				echo   "Error: ".$error."<BR>";
			}
		}
		else{
			echo  $error;
		}
	}
	else {
		echo "Error: project id missing from refering URL.";
	}
}
else
{
	echo "Error: project id missing from refering URL.";
}

gen_footer();
?>