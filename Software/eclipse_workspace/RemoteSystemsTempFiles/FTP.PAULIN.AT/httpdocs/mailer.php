<?php
// ----------------------------------------- 
//  The Web Help .com
// ----------------------------------------- 

// load the variables form address bar
$name = $_REQUEST["name"];
$subject = $_REQUEST["subject"];
$message = $_REQUEST["message"];
$from = $_REQUEST["from"];
$verif_box = $_REQUEST["verif_box"];

// remove the backslashes that normally appears when entering " or '
$name = stripslashes($name); 
$message = stripslashes($message); 
$subject = stripslashes($subject); 
$from = stripslashes($from); 

// check to see if verificaton code was correct
if(md5($verif_box).'a4xn' == $_COOKIE['tntcon']){
	// if verification code was correct send the message and show this page
	$message = "Subject: ".$subject."\n\n".$message;
	$message = "Email: ".$from."\n\n".$message;
	$message = "Name: ".$name."\n\n".$message;
	mail("contact@yaha-project.org", 'House contact: '.$subject, $_SERVER['REMOTE_ADDR']."\n\n".$message, "From: $from");
	// delete the cookie so it cannot sent again by refreshing this page
	setcookie('tntcon','');
} else {
	// if verification code was incorrect then return to contact page and show error
	header("Location:".$_SERVER['HTTP_REFERER']."?subject=$subject&from=$from&message=$message&wrong_code=true");
	exit;
}
?>

<!DOCTYPE HTML>
<!--
	Ion by TEMPLATED
	templated.co @templatedco
	Released for free under the Creative Commons Attribution 3.0 license (templated.co/license)
-->
<html>
	<head>
		<title>Yaha Project - Contact</title>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<!-- Include meta tag to ensure proper rendering and touch zooming -->
		<meta name="viewport" content="width=device-width, initial-scale=1">

		<!--[if lte IE 8]><script src="js/html5shiv.js"></script><![endif]-->
		<script src="js/jquery.min.js"></script>
		<script src="js/skel.min.js"></script>
		<script src="js/skel-layers.min.js"></script>
		<script src="js/init.js"></script>
		<noscript>
			<link rel="stylesheet" href="css/skel.css" />
			<link rel="stylesheet" href="css/style.css" />
			<link rel="stylesheet" href="css/style-xlarge.css" />
		</noscript>
	</head>
	<body id="top">

		<!-- One -->
			<section id="one" class="wrapper style1">
				<header class="major">
					<h2>Vielen Dank</h2>
				</header>
				<div class="container">
					<section>
						<p style="text-align:center;">
							Wir melden uns in Kürze.
						</p>
					</section>		
				</div>
			</section>		
		
		<!-- Footer -->
			<footer id="footer">
				<div class="container">
					<ul class="copyright">
						<li>&copy; Werner Paulin. All rights reserved.</li>
						<li>Design: <a href="http://templated.co">templated</a></li>
					</ul>
				</div>
			</footer>

	</body>
</html>