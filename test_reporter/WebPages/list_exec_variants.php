<?php
include_once("assist.php");
gen_head("Variant List", "style.css");
$error = NULL;

if (isset($_GET["project"])){
	if (isset($_GET["exec"])){
		$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);

		if ($sql_handle != NULL) {
			$query = 'SELECT variant_exec.variant_exec_id, variant_exec.exec_time_secs, variant_exec.created, variant_root.variant, arch.name as arch, target.name as target FROM variant_exec, variant_root, arch, target WHERE target.target_id=variant_root.fk_target_id and arch.arch_id=variant_root.fk_arch_id and variant_root.variant_root_id=variant_exec.fk_variant_root_id and hide_enum="no" and fk_exec_id='.$_GET["exec"];

			$result = sql_query($sql_handle, $query, $error);

			if ($result) {
				$rows = $result->fetchall();

				if (count($rows) > 0){

					echo '<table align="center">';

					foreach($rows as $row) {
						echo '<tr>';
						echo '<td>';
						echo $row["variant_exec_id"];
						echo '</td>';
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
						echo $row["exec_time_secs"];
						echo '</td>';
						echo '<td>';
						echo $row["created"];
						echo '</td>';

						echo '</tr>';
					}

					echo '</table>';
				}
				else{
					echo "There are no variants associted with the choosen exec.";
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
	else {
		echo "Error: Exec id is missing.";
	}
}
else {
	echo "Error: project id missing from refering URL.";
}

gen_footer();
?>