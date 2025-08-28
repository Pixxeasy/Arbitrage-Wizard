import { Box, Heading,  Tabs, TabList, TabPanels, Tab, TabPanel } from "@chakra-ui/react";
import ArbitrageList  from "../components/CurrentArbitrages"
import ConfigList from "../components/ConfigSettings"
import ArbitrageHistoryList from "../components/HistoricArbitrages.tsx";

function Dashboard() {
    return (
        <Box p={6}>
            <Heading>Arbitrage Wizard</Heading>
            <Tabs isFitted variant='enclosed-colored' defaultIndex={0} colorScheme='purple' isLazy={true}>
                <TabList>
                    <Tab>Current</Tab>
                    <Tab>History</Tab>
                    <Tab>Settings</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <ArbitrageList />
                    </TabPanel>
                    <TabPanel>
                        <ArbitrageHistoryList />
                    </TabPanel>
                    <TabPanel>
                        <ConfigList />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
}

export default Dashboard;