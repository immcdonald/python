<?php
include_once("assist.php");
include_once("db_helper.php");
gen_head("DB Size Information", "style.css");
$error = NULL;


if (isset($_GET["schema"])) {
	$sql_handle = get_sql_handle($db_path, $_GET["schema"], $db_user_name, $db_password, $error);
	if ($sql_handle != NULL){
		$query = 'SELECT table_name AS "Tables", 
round(((data_length + index_length) / 1024 / 1024), 2) "Size in MB" 
FROM information_schema.TABLES 
WHERE table_schema = "'.$_GET["schema"].'"
ORDER BY (data_length + index_length) DESC;';

		$data= sql_query($sql_handle, $query, $error);

		echo '<table align="center" cellpadding="3">';
		echo '<tr><th>Tables</th><th>Size in MB</th></tr>';
		foreach($data->fetchall() as $row){
			echo '<tr>';
			echo '<td>';
			echo $row["Tables"];
			echo '</td>';			
			echo '<td>';
			echo $row["Size in MB"];
			echo '</td>';					
			echo '</tr>';
		}
		echo '</table>';
	}
	else{
		echo "Failed to connect to the mysql server.";
	}
}
else{
	die("You did not provide a table name");
}

gen_footer();
?>
