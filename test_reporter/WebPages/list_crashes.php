<?php
include_once("assist.php");
gen_head("Crash List", "style.css");
$error = NULL;

$hide_known_crashes = True;

if (isset($_GET["hide_known"])) {
	if ($_GET["hide_known"] == "on"){
		$hide_known_crashes = True;
	}
	else{
		$hide_known_crashes = False;
	}
}


if (isset($_GET["project"])) {
	if (isset($_GET["exec"])) {
		$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

		if ($sql_handle != NULL) {
			// First get the line marker type id for the different crashes.
			$query = 'SELECT line_marker_type_id, name FROM line_marker_type WHERE name="kdump" or name="kernel_start" or name="process_seg" or name="shutdown"';

			$line_marker_type_results =  sql_query($sql_handle, $query, $error);

			if ($line_marker_type_results) {

				$line_types_rows = $line_marker_type_results->fetchall();

				$crash_line_marker_type_string = "";

				$line_marker_id_to_string = array();

				foreach ($line_types_rows as $row) {

					$line_marker_id_to_string[$row["line_marker_type_id"]] = $row["name"];

					if (strlen($crash_line_marker_type_string) > 0){
						$crash_line_marker_type_string .= ' or fk_line_marker_type_id='.$row["line_marker_type_id"];
					}
					else {
						$crash_line_marker_type_string = 'fk_line_marker_type_id='.$row["line_marker_type_id"];
					}
				}

				# Now get the sub_types

				$query = 'SELECT line_marker_sub_type_id, name from line_marker_sub_type';

				$sub_type_result = sql_query($sql_handle, $query, $error);


				if ($sub_type_result){

					$sub_type_data_rows = $sub_type_result->fetchall();

					$sub_type = array();

					foreach($sub_type_data_rows as $sub_type_data){
						$sub_types[$sub_type_data["line_marker_sub_type_id"]] = $sub_type_data["name"];
					}

					// Now get line marker lines that have crash types
					if ($hide_known_crashes=="yes"){
						echo "Hiding known Crashes";
						$query = 'SELECT line_marker_id, fk_crash_known_id, fk_attachment_id, fk_line_marker_type_id, fk_line_marker_sub_type_id, fk_test_exec_id, start, end FROM view_line_marker_with_exec_id, crash_exec WHERE crash_exec.known_crash_id IS NULL and crash_exec.fk_line_marker_id = view_line_marker_with_exec_id.line_marker_id and fk_exec_id='.$_GET["exec"].' and ('.$crash_line_marker_type_string.') ORDER BY line_marker_id;';
					}
					else
					{	echo "should give all crashes...";
						$query = 'SELECT line_marker_id, fk_crash_known_id, fk_attachment_id, fk_line_marker_type_id, fk_line_marker_sub_type_id, fk_test_exec_id, start, end FROM view_line_marker_with_exec_id, crash_exec WHERE crash_exec.fk_line_marker_id = view_line_marker_with_exec_id.line_marker_id and fk_exec_id='.$_GET["exec"].' and ('.$crash_line_marker_type_string.') ORDER BY line_marker_id;';
					}

					$crash_result = sql_query($sql_handle, $query, $error);

					if ($crash_result) {
						$line_marker_rows = $crash_result->fetchall();

						# now from the view select test information

						echo '<table align="center" border="2">';
						echo '<tr>';

						echo '<th>';
						echo "Link";
						echo '</th>';

						echo '<th>';
						echo "Type";
						echo '</th>';

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
						echo "Test Path";
						echo '</th>';

						echo '<th>';
						echo "Test Name";
						echo '</th>';

						echo '<th>';
						echo "Test Params";
						echo '</th>';

						echo '<th>';
						echo "Result";
						echo '</th>';

						echo '<th>';
						echo "Known Crash ID";
						echo '</th>';

						echo '</tr>';

						foreach($line_marker_rows as $line_marker_row ){
							echo '<tr>';

							$query = 'SELECT result_tag_name, target, arch, variant, test_suite, exec_path, test_name, params, fk_test_suite_root_id, fk_test_root_id FROM view_test_exec WHERE test_exec_id='.$line_marker_row["fk_test_exec_id"];
							$test_data_result = sql_query($sql_handle, $query, $error);

							if ($test_data_result) {
								$test_data = $test_data_result->fetchall();

								echo '<td>';
								echo '<a href="crash_view.php?project='.$_GET["project"].'&exec='.$_GET["exec"].'&lm_id='.$line_marker_row["line_marker_id"].'&attach_id='.$line_marker_row["fk_attachment_id"].'&start='.$line_marker_row["start"].'&end='.$line_marker_row["end"].'&test_exec_id='.$line_marker_row["fk_test_exec_id"].'&lm_type='.$line_marker_id_to_string[$line_marker_row["fk_line_marker_type_id"]].'&lm_type_id='.$line_marker_row["fk_line_marker_type_id"].'&sub_type='.$sub_types[$line_marker_row["fk_line_marker_sub_type_id"]].'&sub_type_id='.$line_marker_row["fk_line_marker_sub_type_id"].'&target='.$test_data[0]["target"].'&arch='.$test_data[0]["arch"].'&variant='.$test_data[0]["variant"].'&suite='.$test_data[0]["test_suite"].'&exec_path='.$test_data[0]["exec_path"].'&test_name='.$test_data[0]["test_name"].'&params='.$test_data[0]["params"].'&result='.$test_data[0]["result_tag_name"].'&test_suite_root_id='.$test_data[0]["fk_test_suite_root_id"].'&test_root_id='.$test_data[0]["fk_test_root_id"].'&crash_known_id='.$line_marker_row["fk_crash_known_id"].'" >'.$line_marker_row["line_marker_id"].'</a>';
								echo '</td>';

								echo '<td>';

								if ($line_marker_id_to_string[$line_marker_row["fk_line_marker_type_id"]] == "process_seg"){
									echo $sub_types[$line_marker_row["fk_line_marker_sub_type_id"]];
								}
								else{
									echo $line_marker_id_to_string[$line_marker_row["fk_line_marker_type_id"]];
								}

								echo '</td>';
								echo '<td>';
								echo $test_data[0]["target"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["arch"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["variant"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["test_suite"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["exec_path"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["test_name"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["params"];
								echo '</td>';

								echo '<td>';
								echo $test_data[0]["result_tag_name"];
								echo '</td>';

								echo '<td>';
								echo $line_marker_row["fk_crash_known_id"];
								echo '</td>';
								echo '</tr>';

							}
							else{
								echo '<td>';
								echo $error;
								echo '</td>';
							}
							echo '</tr>';
						}
						echo "</table>";
					}
					else {
						echo $error;
					}

				}
				else
				{
					echo $error;
				}
			}
			else {
				echo $error;
			}
		}
		else {
			echo $error;
		}
	}
	else {
		echo "Error: Exec id is missing.";
	}
}
else {
	echo "Error: project id missing from refering URL.";
}

gen_footer();
?>