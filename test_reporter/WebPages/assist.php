<?php
$schema_name="qa_db";
ini_set('memory_limit', '4000M');

$db_user_name = "root";
$db_password = "q1!w2@e3#";
$db_path = "localhost";

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
	$stmt = NULL;
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


function gen_head($page_title, $css_file_path){
 	echo "<!DOCTYPE html><html><head>";
 	echo '<title>'.$page_title.'</title>';
	echo '<link rel="stylesheet" type="text/css" href="'.$css_file_path.'">';
	echo '</head><body>';
}

function gen_footer(){
	echo "</body>";
	echo "<footer>";
	echo "<hr>";
	$data = shell_exec('uptime');
	$uptime = explode(' up ', $data);
	$uptime = explode(',', $uptime[1]);
	$uptime = $uptime[0].', '.$uptime[1];

	echo ('Current server uptime: '.$uptime.'<BR>');

	$disk_space = number_format(disk_free_space("/")/1024.00, 0 ,".",$thousands_sep = "," );
	echo "Disk Space Available (/): ".$disk_space." MiB <BR>";

	$disk_space = number_format(disk_free_space("/media/BackUp")/1024.00, 0 ,".",$thousands_sep = "," );
	echo "Disk Space Available (USB drive): ".$disk_space." MiB <BR>";

	$load_avg = sys_getloadavg();
	echo "CPU load avg for the last minute: ".($load_avg[0])." &middot; Last 5 minutes: ".($load_avg[1])." &middot; Last 15 minutes: ".($load_avg[2])." <BR>";
	echo "</footer>";
	echo "</html>";
}




function secs_to_h($secs)
{
        $units = array(
                "week"   => 7*24*3600,
                "day"    =>   24*3600,
                "hour"   =>      3600,
                "minute" =>        60,
                "second" =>         1,
        );

	// specifically handle zero
        if ( $secs == 0 ) return "";

        $s = "";

        foreach ( $units as $name => $divisor ) {
                if ( $quot = intval($secs / $divisor) ) {
                        $s .= "$quot $name";
                        $s .= (abs($quot) > 1 ? "s" : "") . ", ";
                        $secs -= $quot * $divisor;
                }
        }

        return substr($s, 0, -2);
}


function jira_create_link($link_name, $summary, $description, $project_id=11420, $issue_type=1,
						  $base_url="https://jira.bbqnx.net"){
	$link = '<a href="';
	$link = $link.$base_url."/secure/CreateIssueDetails!init.jspa?";
	$link = $link."pid=".(string)$project_id;
	$link = $link."&issuetype=".(string)$issue_type;
	$link = $link."&summary=".urlencode($summary);
	$link = $link."&description=".urlencode($description);
	$link = $link.'">';
	$link = $link.$link_name;
	$link = $link.'</a>';
	return $link;
}

function get_test_result_tags($sql_handle, $project_id, &$error) {
	$result_tags = array();
	$query = 'SELECT id, result, comment, html_color FROM test_result_tag WHERE project_id='.$project_id;
	$result = sql_query($sql_handle, $query, $error);

	if ($result){

		foreach($result->fetchall() as $row){
			$result_tags[$row["id"]] = array("result"=>$row["result"], "comment"=>$row["comment"], "color"=>$row["html_color"]);
		}

		if (count($result_tags) > 0){
			return $result_tags;
		}
		else{
			return NULL;
		}
	}
	else{
		return NULL;
	}
}

function get_test_lexicon($sql_handle, $project_id, &$error) {
	$test_lexicon = array();
	$query = 'SELECT id, test_path, test_name, test_params FROM test_lexicon WHERE project_id='.$project_id;
	$result = sql_query($sql_handle, $query, $error);

	if ($result){
		foreach($result->fetchall() as $row){
			$test_lexicon[$row["id"]] = array("path"=>$row["test_path"], "test_name"=>$row["test_name"],"params" =>$row["test_params"]);
		}

		if (count($test_lexicon) > 0){
			return $test_lexicon;
		}
		else{
			return NULL;
		}
	}
	else{
		return NULL;
	}
}

function get_test_suite($sql_handle, $project_id, &$error) {
	$test_suites = array();
	$query = 'SELECT id, suite_name, project_id, description, added, user_name FROM test_suite WHERE project_id='.$project_id;
	$result = sql_query($sql_handle, $query, $error);

	if ($result){
		foreach($result->fetchall() as $row){
			$test_suites[$row["id"]] = array("name"=>$row["suite_name"], "project_id"=>$row["project_id"],"description" =>$row["description"], "added" =>$row["added"], "user_name" =>$row["user_name"]);
		}

		if (count($test_suites) > 0){
			return $test_suites;
		}
		else{
			return NULL;
		}
	}
	else{
		return NULL;
	}
}

function make_select_options($sql_handle, $query, $value_field_name, $display_field_name, $selected, &$error, $add=NULL){
	$result = sql_query($sql_handle, $query, $error);

	$options = "";
	if ($result) {

		$data = $result->fetchall();

		if (is_array($add)){
			if (count($add) > 0) {
				$data = $add + $data;
			}
		}

		foreach($data as $item){
			if ($item[$value_field_name] == $selected){
				$options = $options.'<option value="'.$item[$value_field_name].'" selected >'.$item[$display_field_name].'</option>';
			}
			else{
				$options = $options.'<option value="'.$item[$value_field_name].'">'.$item[$display_field_name].'</option>';
			}
		}
	}
	else{
		echo $query." -> ".$error;
		return "";
	}

	return $options;
}


function smart_table_header($properties, &$header, &$orderby, $more_orderby=""){
	/* reminder your css file must have

	table.non_default {
    float: right;
	}

	for this code to work.
	*/

	$parts = parse_url($_SERVER["REQUEST_URI"]);
	$query_parts = array();

	if (array_key_exists("query", $parts)){
		parse_str($parts["query"], $query_parts);
	}
	$orderby = NULL;
	$direction = NULL;

	$base_order_by = "";
	$orderby = "";
	$header = "";

	$base_url = "";

	if (array_key_exists("orderby", $query_parts)){
		$base_order_by = $query_parts["orderby"];
		$orderby = " ORDER BY ".$base_order_by;
		unset($query_parts["orderby"]);

	}

	if (array_key_exists("direction", $query_parts)){
		$direction = $query_parts["direction"];
		unset($query_parts["direction"]);

		if (strlen($orderby) > 0){
			$orderby = $orderby." ".$direction;
		}
	}

	if ((strlen($orderby) > 0) && (strlen($more_orderby)>0))
	{
		$orderby = $orderby.", ".$more_orderby;
	}


	//rebuild the query
	$query = "?";

	foreach(array_keys($query_parts) as $key){
		if (is_array($query_parts[$key])){
			foreach($query_parts[$key] as $element){
				if (strlen($query) > 1){
					$query = $query."&";
				}
				$query = $query.$key."[]=".urlencode($element);
			}
		}
		else{
			if (strlen($query) > 1){
				$query = $query."&";
			}
			$query = $query.$key."=".urlencode($query_parts[$key]);
		}
	}

	if (array_key_exists("path", $parts)){
		$base_url = $base_url.$parts["path"];
	}

	if (strlen($query)>0){
		$base_url = $base_url.$query;
	}
	//<span style="font-size:6px"><table border=0 class="non_default"><tr><td><a href="./list_tracked_tests.php?order_by='.$key.'&order_direction=ASC">&#9650;</a></td></tr><tr><td><a href="./list_tracked_tests.php?order_by='.$key.'&order_direction=DESC">&#9660;</a></td></tr> </table></span>
	// &orderby=id&direction=asc

	foreach($properties as $property){
		$arrows = '';

		if ($property["db_name"] != NULL) {
			$arrows = $arrows.'<span style="font-size:6px">';
			$arrows = $arrows.'<table border=0 class="non_default"><tr>';

			$arrows = $arrows.'<td><a href="'.$base_url.'&orderby='.$property["db_name"].'&direction=asc';
			$arrows = $arrows.'">&#9650;</a></td></tr><tr>';
			$arrows = $arrows.'<td><a href="'.$base_url.'&orderby='.$property["db_name"].'&direction=desc';
			$arrows = $arrows.'">&#9660;</a></td></tr>';
			$arrows = $arrows.'</table></span>';
		}
		$header = $header.'<th>';
		if ($property["db_name"]==$base_order_by){
			$header = $header.'<span>'.$arrows."<u>".$property["display"]."</u>"."</span>";
		}
		else{
			$header = $header.$arrows.$property["display"];
		}

		$header = $header.'</th>';
	}
}

function count_digit($number) {
	return strlen((string) $number);
}


function display_sources($exec_id){
	global $db_password, $db_user_name, $db_path, $schema_name;
	$error = NULL;

	$sql_handle = get_sql_handle($db_path, $schema_name, $db_user_name, $db_password, $error);

	if ($sql_handle != NULL) {
		$query = 'SELECT type, src_desc, url, unique_id FROM sources where exec_id='.$exec_id;
		$result = sql_query($sql_handle, $query, $error);

		if ($result){
			$src_data = $result->fetchall();
			$table = "";
			$table .= '<script type="text/javascript">'.PHP_EOL;
			$table .= 'google.load("visualization", "1", {packages:["table"]});'.PHP_EOL;
			$table .= 'google.setOnLoadCallback(drawTable);'.PHP_EOL;

			$table .= 'function drawTable() {'.PHP_EOL;
			$table .= 'var data = new google.visualization.DataTable();'.PHP_EOL;
			$table .= 'data.addColumn("string", "Type");'.PHP_EOL;
			$table .= 'data.addColumn("string", "Source description");'.PHP_EOL;
			$table .= 'data.addColumn("number", "Reference ID");'.PHP_EOL;

			$table .= 'data.addRows(['.PHP_EOL;

			foreach($src_data as $src){
				$table .= "['";
				$table .= strtoupper($src["type"]);
				$table .= "', {v: '";
				$table .= ucfirst($src["src_desc"]);
				$table .= '\', f: \'<a href="'.$src["url"].'">'.ucfirst($src["src_desc"])."<a>'}";
				$table .= ", ";
				if ($src["type"] == "svn"){
					$table .= "{v: ";
					$table .= $src["unique_id"];
					$table .= ", f: '";
					$table .= '<a href="'.$src["url"].'?p='.$src["unique_id"].'">'.$src["unique_id"];
					$table .= "<a>'}";
				}
				else{
					$table .= $src["unique_id"];
				}

				$table .= "],".PHP_EOL;
			}

			$table .= ']);'.PHP_EOL;
			$table .= 'var table = new google.visualization.Table(document.getElementById("source_table_div"));'.PHP_EOL;
			$table .= 'table.draw(data, {showRowNumber: false, allowHtml: true});'.PHP_EOL;
			$table .= "}".PHP_EOL;
			$table .= '</script>'.PHP_EOL;

			echo $table;
			echo '<center><div class="srcgrid" id="source_table_div"></div></center>';
		}
		else{
			echo $error;
		}
	}
	else{
		echo $error;
	}

}

function show_log($variant_id, $start_line, $end_line, $view_mode, $highlight_line, $title, $test_info, &$error, $show_form, $max_lines=60){
	global $db_password, $db_user_name, $db_path, $schema_name;

	$output = "";

	$left_line_marker = "<";
	$right_line_marker = ">";

	if ($highlight_line >= 0){
		if ($highlight_line <  $start_line){
		 	$start_line	= $highlight_line;
		}

		// Note the line space should be at least as many characters as the line_marker
		$left_line_space = "  ";
		$right_line_space = "";
	}
	else{
		$left_line_space = "";
		$right_line_space = "";
	}


	$sql_handle = get_sql_handle($db_path, $schema_name, $db_user_name, $db_password, $error);

	if ($sql_handle != NULL) {

		$query = "SELECT target, arch, variant, uncompress(log) FROM variant WHERE id =".$variant_id;

		$crash_result = sql_query($sql_handle, $query, $error);

		if ($crash_result){
			$row = $crash_result->fetchall();


			$row = $row[0];


			$log = json_decode($row["uncompress(log)"]);


			if ($end_line == -1){
				$end_line = count($log) -1;
			}

			if ($end_line > count($log)){
				$end_line = count($log) -1;
			}

			if ($show_form){
				$output = $output.'<form method="GET">';
				$output = $output.'<label>From: </label><input type="text" name="start_line" value='.$start_line.'><br>';
				$output = $output.'<label>To: </label><input type="text" name="end_line" value='.$end_line.'><br>';
				$output = $output.'<input type="submit" value="update" name="update">';
				$output = $output.'<input type="hidden" value='.$_GET["variant_id"].' name="variant_id">';
				$output = $output.'<input type="hidden" value='.$view_mode.' name="view_mode">';
				$output = $output.'<input type="hidden" value="'.$title.'" name="title">';
				$output = $output.'</form>';
			}

			$max_lines = min($max_lines, ($end_line-$start_line)+1);


			if ($view_mode == "plain"){
				$output = $output.'<textarea readonly cols="150" rows="'.$max_lines .'">';
				for ($i=$start_line; $i <= $end_line; $i++)	{

					$output = $output.$log[$i]."\n";

				}
				$output = $output."</textarea>";
			}
			else if ($view_mode == "plain_numbered"){
				$output = $output.'<textarea readonly cols="150" rows="'.$max_lines .'">';

				$format = sprintf("%%s%%0%dd%%s: %%s%%s", count_digit($end_line));

				for ($i=$start_line; $i <= $end_line; $i++)	{
					if ($highlight_line == $i){
						$output = $output.sprintf($format, $left_line_marker, $i, $right_line_marker, $log[$i], "\n");
					}
					else{
						$output = $output.sprintf($format,$left_line_space, $i, $right_line_space, $log[$i], "\n");
					}
				}
				$output = $output."</textarea>";
			}

			$output .= '<center><a href="./variant_download?variant_id='.$variant_id.'&start_line='.$start_line.'&end_line='.$end_line.'&test_info='.$test_info.'">Download above log</a></center>';
		}
		else{
			$output = $output.$error;
		}
	}
	else{
		$output = $output.$error;
	}

	return $output;
}

function get_attachment(&$error, $sql_handle, $dir_name, $attachment_id, &$file_name, &$variant_id){
    $rc = True;
    $result = q($error, $sql_handle, "SELECT file_name, uncompress(file_blob) as file_data, variant_id FROM attachment WHERE id=".$attachment_id);

    if ($result) {
        $data = $result->fetchall();

        if (count($data) == 1){
            $data = $data[0];
            $variant_id = $data["variant_id"];
            $file_name = $dir_name."/".$data["file_name"];

            $f_out = fopen($dir_name."/".$data["file_name"], "wb");

            if ($f_out !== FALSE) {

                if (fwrite($f_out, $data["file_data"]) === FALSE) {
                    $rc = False;
                    $error = "fwrite failed.";
                }
                fclose($f_out);
            }
            else{
                $rc = False;
                $error = "Failed to open and write to file ".$file_name;
            }
        }
        else{
            $rc = False;
            $error = "Expected 1 record to be returned for attachment id ".$attachment_id." but ".count($data) ." were returned.";
        }
    }
    else{
        $rc = False;
    }
    return $rc;
}


// this function was taken from http://stackoverflow.com/questions/3349753/delete-directory-with-files-in-it
function deleteDir($dirPath) {
    if (! is_dir($dirPath)) {
        throw new InvalidArgumentException("$dirPath must be a directory");
    }
    if (substr($dirPath, strlen($dirPath) - 1, 1) != '/') {
        $dirPath .= '/';
    }
    $files = glob($dirPath . '*', GLOB_MARK);
    foreach ($files as $file) {
        if (is_dir($file)) {
            self::deleteDir($file);
        } else {
            unlink($file);
        }
    }
    rmdir($dirPath);
}

function objdump(&$error, $symbol_file, $cwd){

    $descriptorspec = array(
               0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
               1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
               2 => array("pipe", "r") // stderr is a file to write to
            );

 	$cmd = "/media/BackUp/svn/qnx_tools_for_web/linux/x86/usr/bin/objdump -x".$symbol_file_name;

}


function get_log($sql_handle, $variant_id, $start_line, $end_line, &$error) {

	$query = "SELECT uncompress(log) as log FROM variant WHERE id =".$variant_id;

	$log_result = sql_query($sql_handle, $query, $error);

	if ($log_result){
		$row = $log_result->fetchall();
		$log_result->closeCursor();
		$row = $row[0];
		$log = json_decode($row["log"]);
		$output = "";

		for ($i=$start_line; $i <= $end_line; $i++){
			$output = $output.$log[$i]."\n";
		}
		return $output;
	}
	else{
		die($error);
	}
}


function kdump_view(&$error, $symbol_attach_id, $kdump_attach_id, &$header, &$bt_data, &$info_reg_data, &$display){
    global $db_path, $schema_name, $db_user_name, $db_password;

    $rc = True;

    $sql_handle = get_sql_handle($db_path, $schema_name, $db_user_name, $db_password, $error);

    if ($sql_handle != NULL) {
        $symbol_variant_id = -1;
        $symbol_file_name = "";
        $kdump_variant_id = -1;
        $kump_file_name = "";
        $dir_name = tempnam(sys_get_temp_dir(), 'kdump_dir');
        // Delete the file so we can recreate it as a directory.
        unlink($dir_name);

        if ($dir_name != FALSE) {
            if(mkdir($dir_name)){
                $rc = get_attachment($error, $sql_handle, $dir_name, $symbol_attach_id, $symbol_file_name, $symbol_variant_id);

                if ($rc){
                    $rc = get_attachment($error, $sql_handle, $dir_name, $kdump_attach_id, $kump_file_name, $kdump_variant_id);

                    if($rc){
                        if ($symbol_variant_id == $kdump_variant_id) {
                            $result = q($error, $sql_handle, "SELECT arch FROM variant WHERE id=".$symbol_variant_id);

                            if ($result){
                                $arch = $result->fetchall();
                                if (count($arch) == 1){
                                    $arch = $arch[0]["arch"];
                                    if ($arch=="arm"){
                                        $arch = "armv7";
                                    }

                                    if (system("gunzip ". $kump_file_name) !== FALSE){
                                        $pos = strrpos($kump_file_name, ".gz");

                                        if ($pos !== FALSE){
                                            $elf_name = substr($kump_file_name,0, $pos);


                                            $descriptorspec = array(
                                                       0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
                                                       1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
                                                       2 => array("pipe", "r") // stderr is a file to write to
                                                    );

                                            $cwd = $dir_name;
                                            $env = array();

                                            $cmd = "/media/BackUp/svn/qnx_tools_for_web/linux/x86/usr/bin/nto".$arch."-gdb ".$symbol_file_name;

                                            $process = proc_open($cmd, $descriptorspec, $pipes, $cwd, $env);

                                            if (is_resource($process)) {
                                                // $pipes now looks like this:
                                                // 0 => writeable handle connected to child stdin
                                                // 1 => readable handle connected to child stdout
                                                // Any error output will be appended to /tmp/error-output.txt
                                                fwrite($pipes[0], "echo target remote | kdserver ".$elf_name."\\n\n");

                                                fwrite($pipes[0], "target remote | kdserver ".$elf_name."\n");

                                                fwrite($pipes[0], "echo [ian_is_totally_awesome_bt]\n");
                                                fwrite($pipes[0], "echo bt\\n\n");
                                                fwrite($pipes[0], "bt\n");
                                                fwrite($pipes[0], "echo [/ian_is_totally_awesome_bt]\n");
                                                fwrite($pipes[0], "echo [ian_is_totally_awesome_info_reg]\n");
                                                fwrite($pipes[0], "echo info reg\\n\n");
                                                fwrite($pipes[0], "info reg\n");
                                                fwrite($pipes[0], "echo [/ian_is_totally_awesome_info_reg]\n");
                                                fwrite($pipes[0], "echo [ian_is_totally_awesome_display]\n");
                                                fwrite($pipes[0], "echo display /100i \$pc-0d40\\n\n");
                                                fwrite($pipes[0], "display /100i \$pc-0d40\n");
                                                fwrite($pipes[0], "echo [/ian_is_totally_awesome_display]\n");
                                                fwrite($pipes[0], "quit\n");

                                                fwrite($pipes[0], "y\n");
                                                fclose($pipes[0]);


                                                $data = stream_get_contents($pipes[1]);
                                                fclose($pipes[1]);

                                                // It is important that you close any pipes before calling
                                                // proc_close in order to avoid a deadlock
                                                $return_value = proc_close($process);

                                                if ($return_value == 0) {
                                                    $pos = strrpos($data, "[/ian_is_totally_awesome_bt]");

                                                    $bt_data = substr($data, 0, $pos);

                                                    $pos = strpos($bt_data, "[ian_is_totally_awesome_bt]");

                                                    $header =  trim($cmd."\n".substr($bt_data, 0,  $pos ));

                                                    $bt_data = trim(substr($bt_data, $pos+strlen("[ian_is_totally_awesome_bt]"), strlen($bt_data)));

                                                    $pos = strrpos($data, "[/ian_is_totally_awesome_info_reg]");

                                                    $info_reg_data = substr($data, 0,  $pos);

                                                    $pos = strpos($info_reg_data, "[ian_is_totally_awesome_info_reg]");

                                                    $info_reg_data = trim(substr($info_reg_data, $pos + strlen("[ian_is_totally_awesome_info_reg]"), strlen($info_reg_data)));

                                                    $pos = strrpos($data, "[/ian_is_totally_awesome_display]");

                                                    $display = trim(substr($data, 0,  $pos));

                                                    $pos = strpos($display, "[ian_is_totally_awesome_display]");

                                                    $display = trim(substr($display, $pos + strlen("[ian_is_totally_awesome_display]"), strlen($display)));
                                                }
                                                else{
                                                    $error = "gdb process returned ".$return_value;
                                                    $rc = False;
                                                }
                                            }
                                            else{
                                                $error = "Failed to start gdb process";
                                                $rc = False;
                                            }
                                        }
                                        else{
                                            $error = "Failed to find .gz position in filename";
                                            $rc = False;
                                        }
                                    }
                                    else{
                                        $error =  "gunzip of ".$kump_file_name." failed.";
                                        $rc = False;
                                    }
                                }
                                else{
                                    $error = "Expexted to get back one arch from the database but instead got ".count($arch);
                                    $rc = False;
                                }
                            }
                            else{
                                $rc = False;
                            }
                        }
                        else{
                            $error = "The variant id of the symbol file and the kdump file do not match.";
                            $rc = False;
                        }
                    }
                    else{
                        $rc = False;
                    }
                }
                else{
                    $rc = False;
                }
                deleteDir($dir_name);
            }
            else{
                $error =  "Failed to make directory ".$dir_name."\n";
                $rc = False;
            }
        }
        else{
            $error = "Failed to create a tempary working directory to store files in.\n";
            $rc = False;
        }
    }
    else{
        dir($error);
    }
    return $rc;
}

?>
