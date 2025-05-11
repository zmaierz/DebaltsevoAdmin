<?php
	include($_SERVER["DOCUMENT_ROOT"] . "/engine/kernel.php");
	$app = new Kernel();
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debaltsevo Web | Developer version</title>
    <?php
        $app->showGeneralLayout();
    ?>
</head>
    <body>
        <?php
			$app->ShowHeader();
		?>
        <div class="container">
            <div class="content">
                <?php
                    $page = $_GET["page"];

                    echo $app->getPageContent(basename(__DIR__), $page);
                ?>
            </div>
        </div>
        <?php
			$app->ShowFooter();
		?>
    </body>
</html>