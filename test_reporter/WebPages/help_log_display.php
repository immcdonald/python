<?php
include_once("assist.php");
$error = NULL;






function get_text_line_array_for_line_marker(&$error, $sql_handle, $line_marker_id, &$start_line, &$end_line) {
	$file_data = NULL;

	$query = 'SELECT * FROM line_marker WHERE line_marker_id = '.$line_marker_id;

	$result = sql_query($sql_handle, $query, $error);

	if ($result){
		$rows = $result->fetchall();

		$start = $rows[0]["start"];
		$end = $rows[0]["end"];

		if ($start_line >= 0){
			$start = $start_line;
		}
		else{
			$start_line = $start;
		}

		if ($end_line >= 0){
			$end = $end_line;
		}
		else{
			$end_line = $end;
		}

		if ($start > $end){
			$start = $end;
		}

		$query = 'SELECT storage_rel_path, base_file_name, src_ext, storage_ext, attach_path FROM attachment, project_child WHERE attachment.fk_project_child_id = project_child.project_child_id and attachment_id='.$rows[0]["fk_attachment_id"];

		$result = sql_query($sql_handle, $query, $error);

		if ($result){
			$attach_rows = $result->fetchall();

			$ext = $attach_rows[0]["storage_ext"];

			if ($attach_rows[0]["src_ext"] != $attach_rows[0]["storage_ext"]){
				$ext = $attach_rows[0]["src_ext"].$attach_rows[0]["storage_ext"];
			}

			$storage_name = $attach_rows[0]["attach_path"]."/".$attach_rows[0]["storage_rel_path"]."/".$attach_rows[0]["base_file_name"].$ext;

			if ($attach_rows[0]["storage_ext"] == ".gz"){
				$file = gzopen($storage_name, 'rb');

				$buffer = "";

				while(!gzeof($file)){
					$buffer = gzread($file, 4096);
					$file_data = $file_data.$buffer;
				}

			}
			else{
				$file_data = file_get_contents($storage_name);
			}

			$file_data = explode("\n",$file_data);
			
			$max_lines = count($file_data);

			if ($start > $max_lines){
				$start = $max_lines - 1;
			}

			if ($end > $max_lines){
				$end = $max_lines - 1;
			}

			$file_data = array_slice($file_data, $start, ($end+1)-$start);

			$temp = array();

			$line_index = $start;
			
			// strip the log lines for new lines
			foreach($file_data as &$lines) {
				$temp[$line_index] = str_replace("\r", "", $lines);
				$line_index ++;
			}

			return $temp;
		}
	}

	return $file_data;
}



?>