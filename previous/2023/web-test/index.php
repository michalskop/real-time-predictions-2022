<?php
// output XML based on the current time

header('Content-Type: application/xml');

if (isset($_GET['davka']) & $_GET['davka'] != "") {
  $f = file_get_contents("batches-test-data-2018/" . $_GET['davka'] . ".xml");
  echo($f);
  exit();
}

$delay = "04:10:00"; // calculate GMT difference
$last = 0;

$batches = array_map('str_getcsv', file('batches-test-2018.csv'));

for ($i = 1; $i < count($batches); $i++) {
  // print_r(date("H:i:s", strtotime(substr($batches[$i][1], 11)) - strtotime($delay)));
  // echo("<br/>\n");
  // print_r(date("H:i:s"));
  // echo("<br/>\n\n");
  // die();
  if((date("H:i:s", strtotime(substr($batches[$i][1], 11)) - strtotime($delay))) < date("H:i:s")) {
    $last = $i;
    // print("last: " . $last . "<br/>\n");
    // die();
  }
}

// $last = 38;

$f = file_get_contents("batches-test-data-2018/" . $last . ".xml");
echo($f);

?>