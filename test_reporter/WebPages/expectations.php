<?php
include_once("assist.php");
include_once("help_log_display.php");
include_once("db_helper.php");
gen_head("Expectations", "style.css");
$error = NULL;



function get_expected_results(&$error, &$sql_handle, &$expected_rows, $exec_type){

	$exec_type_id = $rows[0]["fk_exec_type_id"];

	$expected_rows = array();
	$tables = array("test_expected","variant_root", "target");

	$where = array("test_expected.fk_variant_root_id"=>"variant_root.variant_root_id",
				   "variant_root.fk_target_id"=>"target.target_id",
				   "target.fk_project_child_id"=> $_GET["project"],
				   "fk_exec_type_id"=>$exec_type_id);

	$extra_where = "NOW() BETWEEN start_date AND end_date";

	$select = array("test_expected_id", "fk_test_revision_id", "fk_result_tag_id", "start_date", "end_date");

	$rc = select($error, $sql_handle, $expected_rows, $tables, $select, $where, $extra_where);

	if ($rc == OK) {
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
			$select = array("fk_exec_type_id");

			$rc = select($error, $sql_handle, $rows, $tables, $select, $where);

			if ($rc == OK){
				if (count($rows) == 1){
					$exec_type_id = $rows[0]["fk_exec_type_id"];

					# Get all the test results for this exec
					$tables = array("test_exec", "variant_exec");
					$where = array("test_exec.fk_variant_exec_id"=>"variant_exec.variant_exec_id",
								   "variant_exec.fk_exec_id"=>$_GET["exec"]);

					$select = array("test_exec_id", "fk_test_suite_root_id", "fk_test_revision_id", "fk_result_tag_id", "fk_variant_root_id");

					$rc = select($error, $sql_handle, $rows, $tables, $select, $where, NULL, NULL, "fk_variant_root_id ASC, fk_test_suite_root_id ASC, fk_test_revision_id ASC");

					if ($rc == OK){
						show($rows);

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