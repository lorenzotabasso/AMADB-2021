CREATE TABLE `sentiment`
(
    `name` char(16) COLLATE utf8mb4_unicode_ci NOT NULL,
    PRIMARY KEY (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;

CREATE TABLE `lexical_resource`
(
    `id`           int(11)                                NOT NULL AUTO_INCREMENT,
    `name`         varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
    `sentiment_id` char(16) COLLATE utf8mb4_unicode_ci    NOT NULL,
    PRIMARY KEY (`id`),
    KEY `sentiment_id` (`sentiment_id`),
    CONSTRAINT `lexical_resource_ibfk_2` FOREIGN KEY (`sentiment_id`) REFERENCES `sentiment` (`name`) ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;