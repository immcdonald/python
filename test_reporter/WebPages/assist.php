<?php
$schema_name="qa_db";
ini_set('memory_limit', '4000M');

$db_user_name = "root";
$db_password = "q1!w2@e3#";
$db_path = "localhost";
$qnx_tool_path = "/media/BackUp/svn/qnx_tools_for_web/linux/x86/usr/bin";

function show($var, $title=NULL, $rows = 4, $cols = 120, $readonly=False){

	if($title != NULL){
		echo "<center><strong>".$title."</strong></center>";
	}

	if ($readonly){
		echo '<center><textarea rows='.$rows.' cols='.$cols.' readonly>';
	}
	else{
		echo '<center><textarea rows='.$rows.' cols='.$cols.' >';
	}
	print_r($var);
	echo '</textarea></center>';
}

# pass link markers in an array following the form $marked_lines[0] = array("start"=> 14438, "end"=>14445, "mark"=>"=");
function marked_lines_show($lines, $title, $marker_list, $rows=4, $cols=120, $line_number_seperator="", $readonly=False){

	$show_line_number = False;

	if (strlen($line_number_seperator) > 0) {
		$show_line_number = True;	
	}

	echo "<center><strong>".$title."</strong></center>";
	
	if ($readonly){
		echo '<center><textarea rows='.$rows.' cols='.$cols.' readonly>';
	}
	else{
		echo '<center><textarea rows='.$rows.' cols='.$cols.' >';
	}	
	
	foreach ($lines as $index => $value) {

 		if ($show_line_number){
 			echo $index.$line_number_seperator;
 		}

 		foreach(array_reverse($marker_list) as $marker){
 			
 			if (array_key_exists("start", $marker) && array_key_exists("end", $marker) && array_key_exists("mark", $marker)){
 			
 				if (($index >=  $marker["start"]) && ($index <=  $marker["end"])){
 					echo $marker["mark"];
 				}

 			}
 		}

 		echo $value."\n";
	}

	echo '</textarea></center>';
}



function gunzip(&$error, $src_file_path){
	$rc = True;

	if(file_exists($src_file_path)) {
		$file_parts = pathinfo($src_file_path);

		$cmd = array("gunzip", '-c', $src_file_path, ">",  $file_parts["dirname"]."/".$file_parts["filename"]);

		$return = -1;

		$output = system(implode(" ", $cmd), $return);

		if ($return < 0){
			$error = $error = __FUNCTION__.":".__LINE__." The passed file (".$src_file_path.") does not exist or access was denied";
			$rc = False;
		}
	}
	else{
		$error = __FUNCTION__.":".__LINE__." The passed file (".$src_file_path.") does not exist or access was denied";
		$rc = False;
	}
	return True;
}


function dup_get_input_for_form($omit_key_list=NULL){

	if ($omit_key_list != NULL){
		if (is_array($omit_key_list) == False){

			if (is_string($omit_key_list)){
				$pos = strpos($omit_key_list, ",");

				if ($pos === FALSE) {
					$omit_key_list = array($omit_key_list);
				}
				else{
					$omit_key_list = explode(",", $omit_key_list);

					foreach($omit_key_list as &$item){
						$item = trim($item);
					}
				}
			}
			else{
				echo "<BR><BR>ERROR: dup_get_input was passed in a type that it does not support.<BR><BR>";
			}
		}
	}
	else{
		$omit_key_list = array();
	}

	foreach(array_keys($_GET) as $key ){
		if (in_array($key, $omit_key_list) == False) {
			echo '<input type=hidden name="'.$key.'" value="'.$_GET[$key].'" >';
		}
	}
}

function dup_get_input_to_string($omit_key_list=NULL){
	$output = NULL;

	if ($omit_key_list != NULL){
		if (is_array($omit_key_list) == False){

			if (is_string($omit_key_list)){
				$pos = strpos($omit_key_list, ",");

				if ($pos === FALSE) {
					$omit_key_list = array($omit_key_list);
				}
				else{
					$omit_key_list = explode(",", $omit_key_list);

					foreach($omit_key_list as &$item){
						$item = trim($item);
					}
				}
			}
			else{
				echo "<BR><BR>ERROR: dup_get_input was passed in a type that it does not support.<BR><BR>";
			}
		}
	}
	else{
		$omit_key_list = array();
	}

	foreach(array_keys($_GET) as $key ){
		if (in_array($key, $omit_key_list) == False) {
			if (strlen($output) > 0){
				$output .= "&".$key."=".$_GET[$key];
			}
			else{
				$output .= $key."=".$_GET[$key];
			}
		}
	}

	return $output;
}


function dup_get_input($omit_key_list=NULL){

	if ($omit_key_list != NULL){
		if (is_array($omit_key_list) == False){

			if (is_string($omit_key_list)){
				$pos = strpos($omit_key_list, ",");

				if ($pos === FALSE) {
					$omit_key_list = array($omit_key_list);
				}
				else{
					$omit_key_list = explode(",", $omit_key_list);

					foreach($omit_key_list as &$item){
						$item = trim($item);
					}
				}
			}
			else{
				echo "<BR><BR>ERROR: dup_get_input was passed in a type that it does not support.<BR><BR>";
			}
		}
	}
	else{
		$omit_key_list = array();
	}

	foreach(array_keys($_GET) as $key ){
		if (in_array($key, $omit_key_list) == False) {
			echo '<input type=hidden name="'.$key.'" value="'.$_GET[$key].'" >';
		}
	}
}


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




function get_keys_as_string($array){
	$keys = array_keys($array);
	sort($keys);
	$key_string =  '"'.implode('", "', $keys).'"';
	return $key_string;
}

?>
