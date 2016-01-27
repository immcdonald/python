<?php
include_once("assist.php");
gen_head("Regression Runs", "style.css");
$error = NULL;

if (isset($_GET["project"])){
	$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

	if ($sql_handle != NULL) {
		$query = 'SELECT exec.exec_id as id, exec.user_name, exec.comment as comment, exec.created, exec_type.name FROM  exec, exec_type WHERE hide_enum="no" and exec.fk_project_child_id = '.$_GET["project"].' and exec.fk_exec_type_id = exec_type.exec_type_id ORDER BY exec_id DESC';
		$exec_result = sql_query($sql_handle, $query, $error);

		if ($exec_result){

			$rows = $exec_result->fetchall();

			if (count($rows) > 0) {

				echo '<table align="center">';

				foreach($rows as $row) {
					echo "<tr>";

					echo "<td>";
					echo '<a href="report_menu.php?project='.$_GET["project"].'&exec='.$row["id"].'">'.$row["id"]."</a>";
					echo "</td>";

					echo "<td>";
					echo $row["name"];
					echo "</td>";

					echo "<td>";
					echo $row["comment"];
					echo "</td>";

					echo "<td>";
					echo $row["user_name"];
					echo "</td>";

					echo "<td>";
					echo $row["created"];
					echo "</td>";

					echo "<tr>";
				}

				echo '</table>';
			}
			else{
				echo "No execution records found for the selected project.<BR>";
			}
		}
		else{
			echo $error;
		}
	}
	else{
		echo  $error;
	}
}
else
{
	echo "Error: project id missing from refering URL.";
}

gen_footer();
?>