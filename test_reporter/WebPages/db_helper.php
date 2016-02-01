<?php
include_once("assist.php");
$error = NULL;
$show_query = False;

define("OK", 0);
define("ERROR_GENERAL", -1);
define("ERROR_NOT_FOUND", -2);
define("ERROR_MYSQL", -3);
define("ERROR_INVALID_PARAM", -4);
define("ERROR_VALUE_EXISTS", -5);
define("ERROR_BAD_COUNT", -6);

/* ============================================================================================================
 Some Basic MSQL wrappers
==============================================================================================================*/
function get_sql_handle($db_path, $db_shema, $db_user_name, $db_password, &$error){
	$conn = NULL;

	try{
		$conn = new PDO('mysql:host='.$db_path.';dbname='.$db_shema, $db_user_name, $db_password);
	}
	catch(PDOException $e) {
		$conn = NULL;
		$error = 'ERROR: ' . $e->getMessage();
	}

	if ($conn != NULL)
        {
		try{
			$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		}
		catch(PDOException $e) {
			$error = 'ERROR: ' . $e->getMessage();
		}
	}
	return $conn;
}

function sql_query($sql_handle, $query, &$error) {
	global $show_query;

	$stmt = NULL;

	if ($show_query){
		echo $query."<BR>";
	}

	try{
		$stmt = $sql_handle->prepare($query);
	}
	catch(PDOException $e) {
		$stmt = NULL;
		$error = 'ERROR: ' . $e->getMessage();
	}

	if ($stmt != NULL){
		try{
			$stmt->execute();
		}
		catch(PDOException $e) {
			$stmt = NULL;
			$error = 'ERROR: ' . $e->getMessage();
		}
	}
	return $stmt;
}


function q(&$error, $sql_handle, $query_str, &$values=NULL) {
	if ($values != NULL){
		if (is_array($values) === FALSE){
			$errors = 'The values parameter must be passed in the form of an array or NULL';
			return NULL;
		}
	}

	if (strlen($query_str) > 2){
		$query = $sql_handle->prepare($query_str);
		if ($query) {

			$query->execute($values);
			if ($query){
				return $query;
			}
			else{
				$error = $sql_handle->errorInfo();
				$error = $query_str.":<BR>".$error[2];
				return NULL;
			}
		}
		else{
			$error = $sql_handle->errorInfo();
			$error = $query_str.":<BR>".$error[2];
			return NULL;
		}
	}
	else{
		$error = "The query string is to short.";
		return NULL;
	}
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
						$pos = strpos(strtolower(trim($value)), "compress(");

						if ((strtolower($value) != "now()") && ($pos !== 0)){
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

function update(&$error, $sql_handle, $table, $update_dict, $where_data, $where_string=NULL){
	$rc = OK;

	if (is_array($update_dict)) {

		if (is_array($where_data)){
			$where = "";
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
			} // end of foreach(keys($where_data) as $key)

			$rc = field_length_check($error, "table", $table, 0, 65);
			$set = "";
			if ($rc == OK) {
				$fields = array_keys($update_dict);


				foreach($fields as $field){
					# checking the size of the field name.
					$rc = field_length_check($error, $field, $field, 0, 65);

					if ($rc == OK){
						$value = $update_dict[$field];

						if (is_string($value)) {
							$pos = strpos(strtolower(trim($value)), "compress(");

							if ((strtolower($value) != "now()") && ($pos !== 0)){
								$value = '"'.addslashes($value).'"';
							}
						}

						if (strlen($set) > 0){
							$set = $set.", ";
						}
						$set = $set.$field."=".$value;
					}
					else{
						break;
					}
				}
			}

			if ($rc == OK){
				$query = 'UPDATE '.$table.' SET '.$set." WHERE ".$where;
				$result =  sql_query($sql_handle, $query, $error);

				if ($result){
					$result->closeCursor();
				}
				else{
					$rc = ERROR_MYSQL;
				}
			}
		}
		else{
			$rc = ERROR_INVALID_PARAM;
			$error = "Error: where_array variatable must be an array.";

		}
	}
	else{
		$rc = ERROR_INVALID_PARAM;
		$error = "Error: update_dict variatable must be an array.";
	}
	return $rc;
}



/* ============================================================================================================
 Some queries to help pull information from the database.
==============================================================================================================*/
function get_root_projects(&$error, $sql_handle, &$rows) {
	$rc = select($error, $sql_handle, $rows, "project_root", "*");
	return $rc;
}

function get_crash_known_with_bug_info(&$error, $sql_handle, &$rows, $where_array, $where_string=NULL){
	# remember not all known crashes will have bugs, if the crash was intentional.

	$rc = OK;
	$rows  = array();
	$select = array("crash_known_id", "fk_crash_type_id", "fk_test_root_id","fk_test_suite_root_id",
		           "fk_project_bug_id", "type_enum", "resolved", "UNCOMPRESS(regex) as regex", "comment", "created", "html_style_json");

	$tables = array("crash_known");

	$rc =  select($error, $sql_handle, $rows, $tables, $select, $where_array, $where_string);

	if ($rc == OK){
		foreach($rows as &$row){
			if ($row["fk_project_bug_id"] != NULL){
				$sub_rows = array();
				$tables = array("project_bug", "bug_root");

				$where = array("project_bug.project_bug_id"=>$row["fk_project_bug_id"],
							   "project_bug.fk_bug_root_id"=>"bug_root.bug_root_id");

				$select = array("bug_root_id", "recorder_enum", "unique_ref", "summary", "triaged_enum", "resolved_enum", "added_enum");

				$rc =  select($error, $sql_handle, $sub_rows, $tables, $select, $where);

				if ($rc == OK){
					$row["bug_root_id"] = $sub_rows[0]["bug_root_id"];
					$row["recorder_enum"] = $sub_rows[0]["recorder_enum"];
					$row["unique_ref"] = $sub_rows[0]["unique_ref"];
					$row["summary"] = $sub_rows[0]["summary"];
					$row["triaged_enum"] = $sub_rows[0]["triaged_enum"];
					$row["resolved_enum"] = $sub_rows[0]["resolved_enum"];
					$row["added_enum"] = $sub_rows[0]["added_enum"];
				}
			}
			else{
					$row["bug_root_id"] = NULL;
					$row["recorder_enum"] = NULL;
					$row["unique_ref"] =NULL;
					$row["summary"] = NULL;
					$row["triaged_enum"] = NULL;
					$row["resolved_enum"] =NULL;
					$row["added_enum"] =NULL;
			}

		}
	}
	return $rc;
}


function get_variant_exec_id_from_test_exec_id(&$error, $sql_handle,  $test_exec_id, &$variant_exec_id) {
	$rc = OK;
	$rows  = array();
	$select = array("fk_variant_exec_id");
	$tables = array("test_exec");
	$where = array("test_exec_id"=> $test_exec_id);

	$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

	if ($rc ==OK){
		$count = count($rows);

		if ($count == 0){
			$rc = ERROR_NOT_FOUND;
			$error = __FUNCTION__.":".__LINE__."Yeiled no records for test_exec_id:".$test_exec_id;
		}
		else if ($count == 1) {
			$variant_exec_id = $rows[0]["fk_variant_exec_id"];
		}
		else{
			$rc = ERROR_BAD_COUNT;
			$error = __FUNCTION__.":".__LINE__." Returned to many records:".$count." for test_exec_id".$test_exec_id;
		}
	}
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
	$get = array("crash_type_id", "name");

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
				$error = "Warning: (get_crash_type_id) more then one row was returned for ".$crash_type." on project ".$project_child_id."<BR>";
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

/*=====================================================================================================
LINE MARKER FUNCTIONS
=======================================================================================================*/
function get_line_marker_type_id_from_string(&$error, $sql_handle, $line_marker_type){
	$rc = ERROR_GENERAL;
	$rows = array();
	$tables = array("line_marker_type");
	$where = array("name"=>$line_marker_type);
	$select = array("line_marker_type_id");

	$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

	if ($rc == OK) {
		if (count($rows) == 1){
			$rc = $rows[0]["line_marker_type_id"];
		}
		else if (count($rows) == 0){
			$rc = ERROR_NOT_FOUND;
			$error = "(get_line_marker_type_id_from_string) [".$line_marker_type."] not found.";

		}
		else{
			$rc =ERROR_BAD_COUNT;
			$error = "(get_line_marker_type_id_from_string) expected a count of 1 but instead got: ".count($rows);
		}
	}

	return $rc;
}
function get_line_marker_info_for_type(&$error, $sql_handle, &$line_marker_info, $test_exec_id, $line_marker_type){

	$line_marker_type_id = get_line_marker_type_id_from_string($error, $sql_handle, $line_marker_type);

	if ($line_marker_type_id > 0) {
		$rows = array();

		$tables = array("line_marker");
		$where = array("fk_line_marker_type_id"=> intval($line_marker_type_id), "fk_test_exec_id"=> intval($test_exec_id));
		$select = array("*");

		$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

		if ($rc == OK) {
			$count = count($rows);

			if ($count == 0){
				$rc = ERROR_NOT_FOUND;
				$error = __FUNCTION__.":".__LINE__." Yeiled no records.";
			}
			else if ($count == 1) {
				$line_marker_info = $rows[0];
			}
			else{
				$rc = ERROR_BAD_COUNT;
				$error = __FUNCTION__.":".__LINE__." Returned to many records:".$count;
			}
		}
	}
	else{
		$rc = $line_marker_type_id;
	}

	return $rc;
}

function get_info_for_line_marker_id(&$error, $sql_handle, &$row, $lm_id){
	$select = array("line_marker_id", "fk_attachment_id", "line_marker_type_id",
					"line_marker_sub_type_id", "fk_test_exec_id", "start", "end",
					"line_marker.comment as line_marker_comment",
					"line_marker.created as line_marker_created",
					"line_marker_type.name as line_marker_type",
					"line_marker_sub_type.name as line_marker_sub_type",
					);

	$tables = array("line_marker", "line_marker_type", "line_marker_sub_type");

	$where = array("line_marker.fk_line_marker_type_id"=>"line_marker_type.line_marker_type_id",
				   "line_marker.fk_line_marker_sub_type_id"=>"line_marker_sub_type.line_marker_sub_type_id",
				   "line_marker.line_marker_id"=> $lm_id);

	$rows = array();

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where);


	if ($rc == OK){
		$count = count($rows);

		if ($count == 0){
			$rc = ERROR_NOT_FOUND;
			$error = __FUNCTION__.":".__LINE__." ".$lm_id." yeilded no records.";
		}
		else if ($count == 1) {
			$row = $rows[0];
		}
		else{
			$rc = ERROR_BAD_COUNT;
			$error = __FUNCTION__.":".__LINE__." ".$lm_id." returned to many records:".$count;
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
				   "variant_exec.fk_exec_id"=>"exec.exec_id",
				   "variant_exec.fk_variant_root_id"=>"variant_root.variant_root_id",
				   "variant_root.fk_target_id" => "target.target_id",
				   "variant_root.fk_arch_id"=> "arch.arch_id"
				   );

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where, $where_string);

	return $rc;
}

function get_select_master_core(&$error, $sql_handle, &$rows,  $select_list, $where_string=NULL){
	$rc = ERROR_GENERAL;


	if (is_array($select_list) == False){

		if (is_string($select_list)){
			$pos = strpos($select_list, ",");

			if ($pos === FALSE) {
				$select_list = array($select_list);
			}
			else{
				$select_list = explode(",", $select_list);

				foreach($select_list as &$item){
					$item = trim($item);
				}
			}
		}
		else{
			$error= "dup_get_input was passed in a type that it does not support.";
			$rc = ERROR_INVALID_PARAM;
		}
	}


	if (count($select_list) <= 0){
		$error = "Length of select list can not be zero";
		$rc = ERROR_INVALID_PARAM;
	}

	$rows = array();

	$tables = array("line_marker", "crash_exec", "test_exec", "variant_exec", "exec", "test_revision", "variant_root", "target", "arch");

	$where = array("crash_exec.fk_line_marker_id"=>"line_marker.line_marker_id",
				   "line_marker.fk_test_exec_id"=>"test_exec.test_exec_id",
				   "test_exec.fk_variant_exec_id"=>"variant_exec.variant_exec_id",
				   "test_exec.fk_test_revision_id" => "test_revision.test_revision_id",
				   "variant_exec.fk_exec_id"=>"exec.exec_id",
				   "variant_exec.fk_variant_root_id"=>"variant_root.variant_root_id",
				   "variant_root.fk_target_id" => "target.target_id",
				   "variant_root.fk_arch_id"=> "arch.arch_id"
				   );

	$rc = select($error, $sql_handle, $rows, $tables , $select_list, $where, $where_string);

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


/* ============================================================================================================
Attachment helpers
==============================================================================================================*/

// File name here means no extension or path
function get_file_information_for_file_name_and_variant_id(&$error, $sql_handle, &$file_info, $variant_exec_id, $base_file_name, $src_ext=NULL) {
	$rc = OK;

	$select = array("storage_rel_path", "base_file_name", "src_ext", "storage_ext","attach_path");
	$tables = array("attachment", "project_child");

	$where = array("attachment.fk_project_child_id"=>"project_child.project_child_id",
					"fk_variant_exec_id"=>$variant_exec_id,
					"base_file_name"=>$base_file_name);

	if ($src_ext != NULL){
		$where["src_ext"] = $src_ext;
	}

	$rows = array();

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where);

	if ($rc == OK){
		$count = count($rows);

		if ($count == 1){
			$file_info = $rows[0];

			$ext = $file_info["storage_ext"];

			if ($file_info["src_ext"] != $file_info["storage_ext"]){
				$ext = $file_info["src_ext"].$file_info["storage_ext"];
			}
			$file_info["full_path"] = $file_info["attach_path"]."/".$file_info["storage_rel_path"]."/".$file_info["base_file_name"].$ext;
		}
		else{
			$rc = ERROR_BAD_COUNT;
			$error = __FUNCTION__.":".__LINE__." Expected a row count of 1 instead got:".$count." for variant_exec_id: ".$variant_exec_id." and base file name: ".$base_file_name;
		}
	}
}


function get_symbol_file_info_for_variant_exec_id(&$error, $sql_handle, &$file_info, $variant_exec_id){
	$rc = OK;

	$select = array("storage_rel_path", "base_file_name", "src_ext", "storage_ext","attach_path");
	$tables = array("attachment", "project_child");

	$where = array("attachment.fk_project_child_id"=>"project_child.project_child_id",
					"fk_variant_exec_id"=>$variant_exec_id,
					"src_ext"=>".sym");

	$rows = array();

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where);

	if ($rc == OK){
		$count = count($rows);

		if ($count == 1){
			$file_info = $rows[0];

			$ext = $file_info["storage_ext"];

			if ($file_info["src_ext"] != $file_info["storage_ext"]){
				$ext = $file_info["src_ext"].$file_info["storage_ext"];
			}
			$file_info["full_path"] = $file_info["attach_path"]."/".$file_info["storage_rel_path"]."/".$file_info["base_file_name"].$ext;
		}
		else{
			$rc = ERROR_BAD_COUNT;
			$error = __FUNCTION__.":".__LINE__." Expected a row count of 1 instead got:".$count." for variant_exec_id: ".$variant_exec_id;
		}
	}
}


function get_file_info_for_attachment_id(&$error, $sql_handle, &$file_info, $attachment_id) {
	$rc = OK;

	$select = array("storage_rel_path", "base_file_name", "src_ext", "storage_ext","attach_path");
	$tables = array("attachment", "project_child");

	$where = array("attachment.fk_project_child_id"=>"project_child.project_child_id",
					"attachment_id"=>$attachment_id);
	$rows = array();

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where);

	if ($rc == OK){
		$count = count($rows);

		if ($count == 1){
			$file_info = $rows[0];

			$ext = $file_info["storage_ext"];

			if ($file_info["src_ext"] != $file_info["storage_ext"]){
				$ext = $file_info["src_ext"].$file_info["storage_ext"];
			}
			$file_info["full_path"] = $file_info["attach_path"]."/".$file_info["storage_rel_path"]."/".$file_info["base_file_name"].$ext;
		}
		else{
			$rc = ERROR_BAD_COUNT;
			$error = __FUNCTION__.":".__LINE__." Expected a row count of 1 instead got:".$count." for attachment_id ".$attachment_id;
		}
	}
}


function get_file_info_w_lines_for_attachment_id(&$error, $sql_handle, &$file_info, $attachment_id, &$start_line=0 ,&$end_line=-1) {
	$rc = OK;

	if ($start_line < 0){
		$start_line = 0;
	}

	$file_info = array();
	$file_info["storage"] = array();

	$rc = get_file_info_for_attachment_id($error, $sql_handle, $file_info["storage"], $attachment_id);

	if ($rc == OK) {
		$file_data = "";

		if ($file_info["storage"]["storage_ext"] == ".gz"){
			$file = gzopen($file_info["storage"]["full_path"], 'rb');

			$buffer = "";

			while(!gzeof($file)){
				$buffer = gzread($file, 4096);
				$file_data = $file_data.$buffer;
			}
		}
		else{
			$file_data = file_get_contents($file_info["storage"]["full_path"]);
		}

		#Explode on the new lines which are \n. Note: The logs were put in the database using python and read in using the python univeral read mode.
		#So these lines should only have a \n. So no other stripping is required.
		$file_data = explode("\n",$file_data);

		$max_lines = count($file_data);

		if ($max_lines == 0)
		{
			$file_data[0] = "The file is empty!\n";
			$max_lines = 1;
		}

		if ($start_line+1 >= $max_lines){
			$start_line = $max_lines -1;
		}

		if ($end_line+1 >= $max_lines){
			$end_line = $max_lines -1;
		}

		if ($end_line < 0){
			$end_line = $max_lines -1;
		}

		$file_data = array_slice($file_data, $start_line, ($end_line+1)-$start_line);

		$file_info["lines"] = array();

		$line_index = $start_line;

		foreach($file_data as &$lines) {
			$file_info["lines"][$line_index] = $lines;
			$line_index ++;
		}
	}
	return $rc;
}

function get_file_info_for_line_marker_id(&$error, $sql_handle, &$file_info, $line_marker_id, &$start_line=0, &$end_line=-1) {
	$rc = OK;

	$select = array("*");
	$tables = array("line_marker");
	$where = array("line_marker_id" => $line_marker_id);

	$rows = array();

	$rc = select($error, $sql_handle, $rows, $tables , $select, $where);

	if ($rc == OK) {
		$count = count($rows);

		if ($count == 1) {
			$row = $rows[0];

			$rc = get_file_info_w_lines_for_attachment_id($error, $sql_handle, $file_info, $row["fk_attachment_id"], $start_line, $end_line);

		}
		else{
			$rc = ERROR_BAD_COUNT;
			$error = __FUNCTION__.":".__LINE__." Expected a row count of 1 instead got:".$count." for line_marker_id: ".$attachment_id;
		}
	}

	return $rc;
}


function get_kdump_data(){


}



?>