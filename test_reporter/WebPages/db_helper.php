<?php
include_once("assist.php");
$error = NULL;

define("OK", 0);
define("ERROR_GENERAL", -1);
define("ERROR_NOT_FOUND", -2);
define("ERROR_MYSQL", -3);
define("ERROR_INVALID_PARAM", -4);
define("ERROR_VALUE_EXISTS", -5);

function field_length_check(&$error, $field_name, $string, $min=0, $max=65535) {
	$rc = ERROR_GENERAL;

	if (is_string($string) == False){
		$string = (string) $string;
	}

	if (strlen($string) > $min){
		if (strlen($string) <  $max) {
			$rc = OK;
		}
		else{
			$rc = ERROR_INVALID_PARAM;
			$error = "Error: The ".$field_name." value must be less then ".$max;
		}
	}
	else{
		$rc = ERROR_INVALID_PARAM;
		$error = "Error: The ".$field_name." value must be greater then ".$min;
	}

	return $rc;
}

function select(&$error, $sql_handle, &$out_rows, $table, $select_list, $where_data=NULL, $where_string=NULL){
	$rc = ERROR_GENERAL;
	$out_rows = array();

	if (is_array($table) === False) {
		$table = array($table);
	}

	if (is_array($select_list) === False) {
		$select_list = array($select_list);
	}

	foreach($table as $table_name) {
		$pos = strrpos($table_name,".");

		if ($pos !== False){
			 $table_name = substr($table_name, $pos+1, strlen($table_name));
		}

		$rc = field_length_check($error, $table_name, $table_name, 0, 65);

		if ($rc != OK){
			break;
		}
	}

	if ($rc == OK){
		$where = "";

		if ($where_data != NULL) {

			foreach(array_keys($where_data) as $key) {

				# We want to check just the field size so remove any stuff before the .
				# and look for an " as" and remove the " as" and anything after it
				$field_name = $key;
				$pos = strrpos($field_name, ".");

				if ($pos !== False){
					$field_name = substr($field_name, $pos+1, strlen($field_name));
				}

				$pos = strrpos($field_name, " as");

				if ($pos !== False){
					$field_name = substr($field_name, 0, $pos);
				}

				$rc = field_length_check($error, "Where Value:" + $field_name, $field_name, 0, 65);

				if ($rc == OK) {
					$field = "";

					if (is_string($where_data[$key])) {

						if (strtolower($where_data[$key]) != "now()"){
							# Check to see if the value to be written is preceeded by a table name.
							# if it is.. then don't put quotes around it.

							$pos = strpos($where_data[$key],".");

							if ($pos === False){
								$field = $key.'="'.addslashes($where_data[$key]).'"';
							}
							else{
								$item = substr($where_data[$key],0, $pos);

								if (in_array($item, $table)){
									$field = $key.'='.addslashes($where_data[$key]);
								}
								else{
									$field = $key.'="'.addslashes($where_data[$key]).'"';
								}
							}
						}
						else{
							$field = $key."=".$where_data[$key];
						}
					}
					else{
						$field = $key."=".$where_data[$key];
					}

					if (strlen($where) > 0){
						$where = $where." and ".$field;
					}
					else {
						$where = $field;
					}
				}
				else {
					break;
				}
			} // end of foreach(keys($where_data) as $key) {
		}

		if ($rc == OK) {
			$query = 'SELECT '.implode(", ",$select_list)." FROM ".implode(", ", $table);

			if (strlen($where) > 0) {
				$query = $query." WHERE ".$where;
			}

			if ($where_string != NULL) {
				if (strlen($where_string)> 0){
					$query = $query. " and (".$where_string.")";
				}
			}

			echo $query."<BR>";

			$result =  sql_query($sql_handle, $query, $error);

			if ($result){
				$out_rows = $result->fetchall();
				$result->closeCursor();
				$rc = OK;
			}
			else{
				$error = $query." :<BR>".$error;
				$rc = ERROR_MYSQL;
			}

		} // end of if ($rc == OK)
	}

	return $rc;
}

function insert(&$error, $sql_handle, $table, $insert_dict, $check=False) {
	$rc = ERROR_GENERAL;
	if (is_array($insert_dict)) {
		$rc = field_length_check($error, "table", $table, 0, 65);

		if ($rc == OK) {
			$fields = array_keys($insert_dict);
			$values = array();

			foreach($fields as $field){
				$rc = field_length_check($error, $field, $field, 0, 65);

				if ($rc == OK){
					$value = $insert_dict[$field];

					if (is_string($value)) {
						if (strtolower($value) != "now()"){
							$value = '"'.addslashes($value).'"';
						}
					}

					array_push($values, $value);
				}
				else{
					break;
				}
			}

			if ($rc == OK) {

				if ($check) {
					$rows = array();

					$rc = select($error, $sql_handle, $rows, $table, "*", $insert_dict);

					if ($rc == OK) {
						if (count($rows) != 0){
							$error = "Error: Insert skipped these values already exist at id:".$rc;
							$rc = ERROR_VALUE_EXISTS;
						}
					}

				}
				if ($rc == OK) {
					$query = 'INSERT INTO '.$table.' ('.implode(', ',$fields).') VALUES ('.implode(', ', $values).')';

					echo $query."<BR>";

					$result = sql_query($sql_handle, $query, $error);

					if ($result) {
						$rc = $sql_handle->lastInsertId();
						$result->closeCursor();
					}
					else {
						$error = $query." :<BR>".$error;
						$rc = ERROR_MYSQL;
					}
				}
			}
		}
	}
	else {
		$rc = ERROR_INVALID_PARAM;
		$error = "Error: insert_dict variatable must be an array.";
	}
	return $rc;
}

function get_root_projects(&$error, $sql_handle, &$rows) {
	$rc = select($error, $sql_handle, $rows, "project_root", "*");
	return $rc;
}

function get_project_root_and_child(&$error, $sql_handle, &$rows) {
	$tables = array("project_root", "project_child");
	$where = array("project_child.fk_project_root_id"=>"project_root.project_root_id");
	$get = array("project_root.project_root_id",
				 "project_root.name as root_name",
				 "project_root.comment as root_comment",
				 "project_root.created as root_created",
				 "project_child.project_child_id",
				 "project_child.name as child_name",
				 "project_child.comment as child_comment",
				 "project_child.created as child_created");


	$rc = select($error, $sql_handle, $rows, $tables, $get, $where);
	return $rc;
}

function get_crash_types(&$error, $sql_handle, &$rows, $project_child_id){
	$rc = ERROR_GENERAL;
	$tables = array("crash_type");
	$where = array("fk_project_child_id"=>$project_child_id);
	$get = array("crash_type_id");

	$rc = select($error, $sql_handle, $rows, $tables, $get, $where);

	return $rc;
}

function get_crash_type_id(&$error, $sql_handle, $project_child_id, $crash_type) {
	$rc = ERROR_GENERAL;
	$select = array("crash_type_id");
	$tables = array("crash_type");
	$where = array("fk_project_child_id"=>$project_child_id);

	$rc = field_length_check($error, "crash type", $crash_type, 0, 46);

	if ($rc == OK){
		$rows = array();

		$where["name"] = $crash_type;
		$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

		if ($rc == OK){

			if (count($rows) == 1){
				$rc = $rows[0]["crash_type_id"];
			}
			else if (count($rows) > 1){
				$rc = $rowsp[0]["crash_type_id"];
				echo "Warning: (get_crash_type_id) more then one row was returned for ".$crash_type." on project ".$project_child_id."<BR>";
			}
			else{
				$rc = ERROR_NOT_FOUND;
				$error = "Error: (get_crash_type_id) ".$crash_type." was not found in the database for project id:".$project_child_id;
			}
		}
	}
	return $rc;
}

function get_exec_list(&$error, $sql_handle, &$rows, $child_root_id){
	$tables = array("exec", "exec_type");
	$where = array("exec.fk_exec_type_id"=>"exec_type.exec_type_id", "fk_project_child_id"=>$child_root_id);
	$get = array("exec.exec_id", "exec_type.name", "exec.user_name", "exec.comment as exec_comment", "exec_type.comment as exec_type_comment");

	$rc = select($error, $sql_handle, $rows, $tables, $get, $where);
	return $rc;
}

function get_bug_root_id(&$error, $sql_handle, $reporter_type, $unique_ref) {
	$rc = ERROR_GENERAL;
	$valid_reporter_types = array("ji", "pr");

	if (in_array($reporter_type, $valid_reporter_types)) {
		$rows = array();
		$where = array("recorder_enum"=>$reporter_type, "unique_ref"=>$unique_ref);

		$rc = select($error, $sql_handle, $rows, "bug_root", "bug_root_id", $where);

		if ($rc == OK)
		{
			if (count($rows) == 0){
				$rc = ERROR_NOT_FOUND;
			}
			elseif(count($rows) == 1){
				$rc = $rows[0]["bug_root_id"];
			}
			else {
				$rc = $rows[0]["bug_root_id"];
				echo "WARNING: (get_bug_root_id) Expected only one row to be returned but got more: ".(count($rows))."<BR>";
			}
		}
	}
	else{
		$error = $reporter_type." is not a valid reporter type";
		$rc = ERROR_INVALID_PARAM;
	}
	return $rc;
}

function add_bug_root(&$error, $sql_handle, $reporter_type, $unique_ref, $summary=NULL, $comment=NULL) {
	$rc = ERROR_GENERAL;

	/* Check to see if this bug already exists */
	$rc = get_bug_root_id($error, $sql_handle, $reporter_type, $unique_ref);

	if ($rc == ERROR_NOT_FOUND) {

		$insert = array();
		$insert["created"]="now()";
		$insert["recorder_enum"] = $reporter_type;

		$rc = field_length_check($error, "unique_ref", $unique_ref, 0, 65535);

		if ($rc == OK) {
			$insert["unique_ref"] = $unique_ref;
		}

		if ($rc == OK){
			if ($summary != NULL){
				$rc = field_length_check($error, "summary", $summary, 0, 65535);
				if ($rc == OK){
					$insert["summary"] = $summary;
				}
			}
		}

		if ($rc == OK){
			if ($comment != NULL){
				$rc = field_length_check($error, "comment", $comment, 0, 65535);
				if ($rc == OK){
					$insert["comment"] = $comment;
				}
			}
		}

		if ($rc == OK) {
			$rc = insert($error, $sql_handle, "bug_root", $insert, False);
		}
	}

	return $rc;
}

function get_project_bug_info(&$error, $sql_handle, &$rows, $reporter_type, $unique_ref, $project_child_id) {
	$rc = ERROR_GENERAL;

	$valid_reporter_types = array("ji", "pr");

	if (in_array($reporter_type, $valid_reporter_types)) {
		$select = array("*");
		$tables = array("bug_root", "project_bug");
		$where = array("project_bug.fk_bug_root_id"=>"bug_root.bug_root_id",  "recorder_enum"=>$reporter_type, "fk_project_child_id"=>$project_child_id);

		$rc = field_length_check($error, "unique_ref", $unique_ref, 0, 65535);

		if ($rc == OK) {
			$where["unique_ref"] = $unique_ref;
		}

		if ($rc == OK){
			$rc = select($error, $sql_handle, $rows, $tables , $select, $where);
		}
	}
	else{
		$error = $reporter_type." is not a valid reporter type";
		$rc = ERROR_INVALID_PARAM;
	}

	return $rc;
}

function add_project_bug(&$error, $sql_handle, $reporter_type, $unique_ref, $project_child_id, $summary=NULL, $comment=NULL, $added_by="other") {

	$rows = array();

	# check and see if the project bug already exists
	$rc = get_project_bug_info($error, $sql_handle, $rows, $reporter_type, $unique_ref, $project_child_id);

	if ($rc == OK) {
		if (count($rows) == 0){

			# This one will check to see if the bug root is there and create it it doesn't..
			$bug_root_id = add_bug_root($error, $sql_handle, $reporter_type, $unique_ref, $summary, $comment);

			if ($bug_root_id > 0) {

					$insert = array("fk_project_child_id"=>$project_child_id, "fk_bug_root_id"=>$bug_root_id, "created"=>"now()", "added_enum"=>$added_by);

					if ($comment != NULL){
						$rc = field_length_check($error, "comment", $comment, 0, 65535);
						if ($rc == OK){
							$insert["comment"] = $comment;
						}
					}

					if ($rc==OK){
						/*
							Set the insert precheck to FALSE here. WE already checked at the top of the function to see if this
							Entry exists.. so we don't want to do it again. Also, this query contains the added by and we would
							want to filter on matches by added_by.
						*/
						$rc = insert($error, $sql_handle, "project_bug", $insert, False);

					}
				}
				else{
					$rc = $bug_root_id;
				}
		}
		else{
			$rc = $rows[0]["project_bug_id"];
		}

	}
	return $rc;
}

function get_master_core(&$error, $sql_handle, &$rows,  $where_string=NULL) {
	$rc = ERROR_GENERAL;

	$rows = array();

	$tables = array("line_marker", "crash_exec", "test_exec", "variant_exec", "exec", "test_revision");

	$select = array("line_marker_id", "crash_exec_id", "fk_attachment_id as attachment_id",
				 "fk_line_marker_type_id as line_marker_type_id",
				 "fk_line_marker_sub_type_id as line_marker_sub_type_id", "start", "end",
				 "fk_crash_type_id as crash_type_id", "fk_crash_known_id as crash_known_id",
				 "test_exec_id", "fk_result_tag_id as result_tag_id", "test_exec.fk_exec_abort_id as test_exec_abort_id",
				 "variant_exec_id", "variant_exec.fk_exec_abort_id as variant_exec_abort_id", "test_revision_id", "test_revision.fk_test_root_id as test_root_id", );

	$where = array("crash_exec.fk_line_marker_id"=>"line_marker.line_marker_id",
				   "line_marker.fk_test_exec_id"=>"test_exec.test_exec_id",
				   "test_exec.fk_variant_exec_id"=>"variant_exec.variant_exec_id",
				   "test_exec.fk_test_revision_id" => "test_revision.test_revision_id",
				   "variant_exec.fk_exec_id"=>"exec.exec_id"
				   );

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where, $where_string);

	echo '<textarea cols="200" rows="20">';
	var_dump($rows);
	echo "</textarea>";

	return $rc;
}


?>