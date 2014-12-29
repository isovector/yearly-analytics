function getMessages() {
    var query = "after:2014/1/1";
    query += " in:anywhere -label:sms -label:call-log -label:chats -label:spam -filename:ics";
    query += " -from:maestro.bounces.google.com -from:unified-notifications.bounces.google.com -from:docs.google.com";
    query += " -from:group.calendar.google.com -from:apps-scripts-notifications@google.com";
    query += " -from:sites.bounces.google.com -from:noreply -from:notify -from:notification";

    var sends = 0;
    var sendWords = 0;
    var recvs = 0;
    var recvWords = 0;
    var convos = 0;

    var conversations = GmailApp.search(query);
    for (var j = 0; j < conversations.length; j++) {
        convos += 1;
        var messages = conversations[j].getMessages()
            for (var i = 0; i < messages.length; i++) {
                var msg = messages[i];

                var wordCount = 0;
                try {
                    wordCount = msg.getPlainBody().split(/\s+/).length;
                } catch(e) {

                }

                if (msg.getFrom().indexOf("maguire") != -1) {
                    sends += 1;
                    sendWords += wordCount;
                } else {
                    recvs += 1;
                    recvWords += wordCount;
                }
            }
    }

    Logger.info("sends: " + sends);
    Logger.info("words: " + sendWords);
    Logger.info("recvs: " + recvs);
    Logger.info("words: " + recvWords);
    Logger.info("convo: " + convos);
};
