<?php
ini_set ( 'max_execution_time', 0);
include_once("assist.php");
include_once("help_log_display.php");
include_once("db_helper.php");
$error = "";

$output_path = "/var/www/boblyboo";
$input_path = "/media/BackUp/regression_data";

function joinPaths() {
	$start_with_slash = False;
    $args = func_get_args();
    $paths = array();

    $arch_counter = 0;
    foreach ($args as &$arg) {
    	$arg = trim($arg);
    	$arg = str_replace("/", DIRECTORY_SEPARATOR, $arg);
    	$arg = str_replace("\\", DIRECTORY_SEPARATOR, $arg);

		if ($arch_counter  == 0){
			if ($arg[0] == DIRECTORY_SEPARATOR) {
				$start_with_slash = true;
			}
		}

        $paths = array_merge($paths, (array)$arg);
        $arch_counter ++;
    }

    $paths = array_map(create_function('$p', 'return trim($p, DIRECTORY_SEPARATOR);'), $paths);

    $paths = array_filter($paths);

    if ($start_with_slash){
    	return DIRECTORY_SEPARATOR.join(DIRECTORY_SEPARATOR, $paths);
    }
    else {
    	return join(DIRECTORY_SEPARATOR, $paths);
    }
}

function mk_dirp($path, $permission=0777, $recursive=false){
	if (file_exists($path) == False){
		return mkdir($path, $permission, $recursive);
	}
	else{
		return True;
	}
}


function archive_2_tree(&$error, $sql_handle, $input_path, $output_path){

	if (file_exists($input_path) == False){
		die($input_path." Does not exist or you do not have permissions.");
	}

	if (mk_dirp($output_path, 0777, true) == False){
		die("mkdir of ".$output_path." failed.");
	}


	# Start by getting all the projects from the database.
	$project_rows = array();
	$tables = array("project");
	$where = NULL;
	$select = array("id", "name");

	$rc = select($error, $sql_handle, $project_rows, $tables, $select, $where, NULL,NULL, "id");

	if ($rc == OK) {

		foreach($project_rows as  $project){
			$project_path = joinPaths($output_path, ucfirst($project["name"]));

			if (mk_dirp($project_path, 0777, true)){
				// now create the exec_id folders for this project.
				$tables = array("exec_tracker");
				$where = array("project_id"=> $project["id"]);
				$select = array("id", "user_name", "created", "description");

				$exec_id_rows = array();
				$rc = select($error, $sql_handle, $exec_id_rows, $tables, $select, $where, NULL, NULL, "id");

				if ($rc == OK) {
					foreach($exec_id_rows as $exec_id_row){
						$exec_path = joinPaths($project_path, sprintf("%09d", $exec_id_row["id"]));

						if (mk_dirp($exec_path, 0777, true)){

						}
						else{
							die("mkdir of ".$exec_path." failed.");
						}
					}
				}
				else{
					die($error);
				}
			}
			else{
				die("mkdir of ".$project_path." failed.");
			}
		}
	}
	else{
		echo $error."<BR>";
	}
}

$sql_handle = get_sql_handle($db_path, "qa_db", $db_user_name, $db_password, $error);

if ($sql_handle != NULL) {
	archive_2_tree($error, $sql_handle, $input_path, $output_path);

}
else{
	die($error);
}


?>
