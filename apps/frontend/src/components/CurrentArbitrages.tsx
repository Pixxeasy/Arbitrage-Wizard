import {
    Alert, AlertDescription,
    AlertIcon, AlertTitle,
    Box,
    Card,
    CardBody,
    Button,
    HStack,
    Icon,
    Skeleton,
    Stack,
    StackDivider,
    Text,
    VStack
} from "@chakra-ui/react";
import {ArbitrageGroup, ArbitrageOpportunity} from "../types/Arbitrage"
import React, {useState} from "react";
import { motion } from "framer-motion";
import {ChevronLeftIcon, ArrowForwardIcon} from "@chakra-ui/icons";
import moment from "moment";
import {useCurrentArbitragesQuery} from "../redux/services/arbitrage";

const ArbitrageOpportunityItem: React.FC<{opportunity: ArbitrageOpportunity}> = ({opportunity}) => (
    <HStack align="center">
        <Text>Kaufpreis: {opportunity.buyPrice.toFixed(4)}</Text>
        <Text>Verkauspreis: {opportunity.sellPrice.toFixed(4)}</Text>
        <Text>Startbetrag: {opportunity.minAmountStart?.toFixed(4)} - {opportunity.maxAmountStart?.toFixed(4)} USDT</Text>
        <Text>Endbetrag: {opportunity.minAmountEnd?.toFixed(4)} - {opportunity.maxAmountEnd?.toFixed(4)} USDT</Text>
        <Text>Profit: {opportunity.minProfit?.toFixed(4)} - {opportunity.maxProfit?.toFixed(4)} USDT</Text>
    </HStack>
)

const ArbitrageGroupItem: React.FC<{group: ArbitrageGroup}> = ({group}) => {

    const [open, setOpen] = useState(false)

    return (
        <>
        <Card variant="filled" bgColor="purple.300" textColor={"white"}>
            <CardBody>
                <HStack align="center" justify="space-between">
                    <Text>Pair: {group.tradingPair}</Text>
                    <Text>
                        {group.buyExchange} <Icon as={ArrowForwardIcon}/> {group.chainName} <Icon as={ArrowForwardIcon}/> {group.sellExchange}
                    </Text>
                    <Button onClick={() => setOpen(!open)} justifySelf={"right"} colorScheme={"purple"}>
                        <motion.div
                            initial={{opacity: 0}}
                            animate={{opacity: 1, rotate: open ? -90 : 0}}
                            transition={{duration: 0.3}}
                        >
                            <Icon as={ChevronLeftIcon} boxSize={6}/>
                        </motion.div>
                    </Button>
                </HStack>
            </CardBody>
        </Card>

                <Box paddingLeft={6}> {open &&
                    group.opportunities.map((op, index) => (
                        <Card mt={3} variant="filled" colorScheme={"purple"} bgColor={"purple.100"}>
                            <CardBody>
                                <ArbitrageOpportunityItem opportunity={op} key={index} />
                            </CardBody>
                        </Card>
                    ))
                }</Box>
        </>
    )
}

function ArbitrageList() {

    const {data, isLoading, isError, isSuccess, error} = useCurrentArbitragesQuery({}, {
        pollingInterval: 30*1000,
        skipPollingIfUnfocused: true,})

    return (
        <VStack
            divider={<StackDivider borderColor='gray.200'/>}
            spacing={4}
            align='stretch'
        >
            <Box justifyContent={"right"}><Text>
                Last Client Update: {isSuccess && moment(data.clientTime).format("HH:mm:ss")}
            </Text>
            <Text>Last Server Update: { isSuccess && moment.utc(data.lastUpdate).local().format("HH:mm:ss")}</Text></Box>
            {
                (isLoading && !data ) && <Stack>
                    <Skeleton height='20px' />
                    <Skeleton height='20px' />
                    <Skeleton height='20px' />
                </Stack>
            }
            {
                (isSuccess && data.arbitrages.length== 0) &&
                <Alert status='info'>
                    <AlertIcon />
                    <AlertTitle>No Arbitrages found :(</AlertTitle>
                    <AlertDescription></AlertDescription>
                </Alert>
            }
            {
                isError &&
                <Alert status='error'>
                    <AlertIcon />
                    <AlertTitle>Error fetching data</AlertTitle>
                    <AlertDescription>{error.error}</AlertDescription>
                </Alert>
            }
            {
              isSuccess &&  data.arbitrages.map((g,index) => (<ArbitrageGroupItem group={g} key={index} />))
            }
        </VStack>
    )
}

export default ArbitrageList;
