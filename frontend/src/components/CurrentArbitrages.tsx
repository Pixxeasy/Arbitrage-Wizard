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
import React, {useState, useEffect} from "react";
import { motion } from "framer-motion";
import {ChevronLeftIcon, ArrowForwardIcon} from "@chakra-ui/icons";
import {useDispatch, useSelector} from "react-redux";
import {arbitrageSelector, clearState, getArbitrage} from "../store/slices/ArbitrageSlice.tsx";
import moment from "moment";

const ArbitrageOpportunityItem: React.FC<{opportunity: ArbitrageOpportunity}> = ({opportunity}) => (
    <HStack align="center">
        <Text>Kaufpreis: {opportunity.buyPrice.toFixed(4)}</Text>
        <Text>Verkauspreis: {opportunity.sellPrice.toFixed(4)}</Text>
        <Text>Startbetrag: {opportunity.minAmountStart.toFixed(4)} - {opportunity.maxAmountStart.toFixed(4)} USDT</Text>
        <Text>Endbetrag: {opportunity.minAmountEnd.toFixed(4)} - {opportunity.maxAmountEnd.toFixed(4)} USDT</Text>
        <Text>Profit: {opportunity.minProfit.toFixed(4)} - {opportunity.maxProfit.toFixed(4)} USDT</Text>
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
    const [lastFetch, setLastFetch] = useState(Date.now())


    const dispatch = useDispatch();
    const { arbitrageGroups, lastUpdate , isFetching, isSuccess, isError, errorMessage } = useSelector(arbitrageSelector);

    useEffect(() => {
        dispatch(getArbitrage())
        const interval = setInterval(() => {
            dispatch(getArbitrage())
        }, 1000*30);

        return () => clearInterval(interval);
    }, []);


    useEffect(() => {
        return () => {
            dispatch(clearState());
        };
    }, []);

    useEffect(() => {
        if (isError) {
            console.log(errorMessage);
            dispatch(clearState());
        }

        if (isSuccess) {
            dispatch(clearState());
            setLastFetch(Date.now())

        }
    }, [isError, isSuccess]);

    return (
        <VStack
            divider={<StackDivider borderColor='gray.200'/>}
            spacing={4}
            align='stretch'
        >
            <Box justifyContent={"right"}><Text>
                Last Client Update: {moment(lastFetch).format("HH:mm:ss")}
            </Text>
            <Text>Last Server Update: {moment(lastUpdate*1000).format("HH:mm:ss")}</Text></Box>
            {
                isFetching && <Stack>
                    <Skeleton height='20px' />
                    <Skeleton height='20px' />
                    <Skeleton height='20px' />
                </Stack>
            }
            {
                arbitrageGroups.length == 0 &&
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
                    <AlertDescription>{errorMessage}</AlertDescription>
                </Alert>
            }
            {
                arbitrageGroups.map((g,index) => (<ArbitrageGroupItem group={g} key={index} />))
            }
        </VStack>
    )

}

export default ArbitrageList;
