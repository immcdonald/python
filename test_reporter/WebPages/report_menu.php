<?php
include_once("assist.php");
gen_head("Report Selection", "style.css");
$error = NULL;

if (isset($_GET["project"])){
	if (isset($_GET["exec"])){
		echo '<a href="list_exec_variants.php?project='.$_GET["project"].'&exec='.$_GET["exec"].'">List exec variants</a><BR>';
		echo '<a href="list_crashes.php?project='.$_GET["project"].'&exec='.$_GET["exec"].'&hide_known=yes" >Crash List</a><BR>';
	}
	else
	{
		echo "Error: Exec id is missing.";
	}
}
else
{
	echo "Error: project id missing from refering URL.";
}

gen_footer();
?>