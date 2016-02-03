<?php
include_once("assist.php");
include_once("db_helper.php");
gen_head("DB Size Information", "style.css");
$error = NULL;

$sql_handle = get_sql_handle($db_path, "project_db", $db_user_name, $db_password, $error);
if ($sql_handle != NULL) {
	$query = 'SELECT table_schema "Data Base Name",
sum( data_length + index_length ) / 1024 /
1024 "Data Base Size in MB",
sum( data_free )/ 1024 / 1024 "Free Space in MB"
FROM information_schema.TABLES
GROUP BY table_schema ; ';

		$data= sql_query($sql_handle, $query, $error);

		echo '<table align="center" cellpadding="3">';
		echo '<tr><th>Data Base Name</th><th>Data Base Size in MB</th><th>Free Space in MB</th></tr>';
		foreach($data->fetchall() as $row){
			echo '<tr>';
			echo '<td>';
			echo '<a href="table_size.php?schema='.$row["Data Base Name"].'">'.$row["Data Base Name"].'</a>';
			echo '</td>';			
			echo '<td>';
			echo $row["Data Base Size in MB"];
			echo '</td>';
			echo '<td>';
			echo $row["Free Space in MB"];
			echo '</td>';						
			echo '</tr>';
		}
		echo '</table>';
}
else{
	echo  $error;
}

gen_footer();
?>
