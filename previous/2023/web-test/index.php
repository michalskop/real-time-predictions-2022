<?php
// output XML based on the current time

header('Content-Type: application/xml');

if (isset($_GET['davka']) & $_GET['davka'] != "") {
  $f = file_get_contents("batches-test-data/" . $_GET['davka'] . ".xml");
  echo($f);
  exit();
}

$delay = "14:00:00"; // calculate GMT difference
$last = 0;

$batches = array_map('str_getcsv', file('batches-test-data.csv'));

for ($i = 1; $i < count($batches); $i++) {
  print_r(date("H:i:s", strtotime(substr($batches[$i][1], 11)) + strtotime($delay)));
  echo("<br/>");
  print_r(date("H:i:s", strtotime(substr($batches[$i][1], 11))));
  echo("<br/>");
  print_r(strtotime(substr($batches[$i][1], 11)));
  echo("<br/>");
  print_r(strtotime($delay));
  die();
  if((date("H:i:s", strtotime(substr($batches[$i][1], 11)) + strtotime($delay))) < date("H:i:s")) {
    $last = $i;
    // echo("<br/>");
    // print($last);
    // die();
  }
}

$f = file_get_contents("batches-test-data/" . $last . ".xml");
echo($f);

?>