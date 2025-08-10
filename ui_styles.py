def get_style_sheet() -> str:
    return """
            #MainWindow {
                background-color: #F8F9FA;
            }
            #ContainerWidget {
                background-color: #FFFFFF;
                border: 1px solid #DEE2E6;
                border-radius: 8px;
            }
            #MainTitle {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 28px;
                font-weight: 600;
                color: #212529;
            }
            #SectionTitle {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 20px;
                font-weight: 600;
                color: #212529;
            }
            #HeaderButton, #ActionButton {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #FFFFFF;
                color: #212529;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
            }
            #HeaderButton:hover, #ActionButton:hover {
                background-color: #F8F9FA;
            }
            #ViewJsonButton {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #E9ECEF;
                color: #212529;
                border: 1px solid #E9ECEF;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
            }
             #ViewJsonButton:hover {
                background-color: #DEE2E6;
                border-color: #DEE2E6;
            }
            #AddServerButton {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #E9ECEF;
                color: #212529;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                font-weight: 500;
            }
            #AddServerButton:hover {
                background-color: #DEE2E6;
            }
            .QFrame#Separator {
                background-color: #E9ECEF;
                height: 1px;
            }
            #GridHeader {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: #495057;
            }
            QLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #212529;
            }
            #StatusOffline {
                background-color: #DC3545;
                color: white;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            #StatusOnline {
                background-color: #28A745;
                color: white;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            #StatusError {
                background-color: #FFC107;
                color: black;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            #Footer {
                background-color: #F8F9FA;
                border-top: 1px solid #DEE2E6;
            }
            #FooterLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #6C757D;
            }
            #NoServersLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 16px;
                color: #6C757D;
                font-style: italic;
                padding: 20px;
            }
        """