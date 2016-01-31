<?php
include_once("assist.php");
include_once("help_log_display.php");
include_once("db_helper.php");

gen_head("Project Selection", "style.css");
$error = NULL;

$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

if ($sql_handle != NULL) {
	$query = 'SELECT project_child_id, project_root.name as root_name, project_child.name as child_name FROM project_root, project_child WHERE project_root.project_root_id = project_child.fk_project_root_id ORDER BY root_name ASC, child_name ASC ';
	$projects_result = sql_query($sql_handle, $query, $error);

	if ($projects_result){
		echo '<form action="list_exec.php" method="GET">';
		echo '<select name="project">';

		foreach($projects_result->fetchall() as $project){
			echo '<option value='.$project["project_child_id"].'>'.$project["root_name"]." - ".$project["child_name"]."</option>";
		}

		echo '</select>';
		echo '<input type="submit" name="select" value="select" />';
		echo '</form>';
	}
	else{
		echo $error;
	}
}
else{
	echo  $error;
}

gen_footer();
?>