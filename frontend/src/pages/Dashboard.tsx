import { Box, Heading,  Tabs, TabList, TabPanels, Tab, TabPanel } from "@chakra-ui/react";
import ArbitrageList  from "../components/CurrentArbitrages"

function Dashboard() {
    return (
        <Box p={6}>
            <Heading>Arbitrage Wizard</Heading>
            <Tabs isFitted variant='enclosed-colored' defaultIndex={0} colorScheme='purple'>
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
                        <p>two!</p>
                    </TabPanel>
                    <TabPanel>
                        <p>history</p>
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
}

export default Dashboard;