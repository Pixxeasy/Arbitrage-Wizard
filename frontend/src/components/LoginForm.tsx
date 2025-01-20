import React, { useState } from 'react';
//import './LoginForm.scss';
import {Field, Formik, useFormik} from "formik";
import {
    Box,
    Button,
    Flex,
    FormControl, FormErrorMessage,
    FormLabel,
    Input,
    VStack
} from "@chakra-ui/react";
import { useDispatch, useSelector } from "react-redux";
import { loginUser, loginSelector, clearState } from '../store/slices/LoginSlice';
import { useEffect } from "react";
import { useNavigate } from "react-router"

const LoginForm: React.FC = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    //const { register, errors, handleSubmit } = useForm();
    const { isFetching, isSuccess, isError, errorMessage } = useSelector(loginSelector);
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
            navigate("/dashboard");
        }
    }, [isError, isSuccess]);

    return (
        <Flex bg="gray.100" align="center" justify="center" h="100vh">
            <Box bg="white" p={6} rounded="md" w={64}>
                <Formik
                    initialValues={{
                        username: "",
                        password: ""
                    }}
                    onSubmit={(data) => {
                        dispatch(loginUser(data))
                    }}
                >
                    {({ handleSubmit, errors, touched }) => (
                        <form onSubmit={handleSubmit}>
                            <VStack spacing={4} align="flex-start">
                                <FormControl>
                                    <FormLabel htmlFor="username">Username</FormLabel>
                                    <Field
                                        as={Input}
                                        id="username"
                                        name="username"
                                        type="input"
                                        variant="filled"
                                    />
                                </FormControl>
                                <FormControl isInvalid={!!errors.password && touched.password}>
                                    <FormLabel htmlFor="password">Password</FormLabel>
                                    <Field
                                        as={Input}
                                        id="password"
                                        name="password"
                                        type="password"
                                        variant="filled"
                                        validate={(value: string) => {
                                            let error;

                                            if (value.length < 4) {
                                                error = "Password must contain at least 6 characters";
                                            }

                                            return error;
                                        }}
                                    />
                                    <FormErrorMessage>{errors.password}</FormErrorMessage>
                                </FormControl>
                                <Button type="submit" colorScheme="purple" width="full">
                                    Login
                                </Button>
                            </VStack>
                        </form>
                    )}
                </Formik>
            </Box>
        </Flex>
    );
};

export default LoginForm;
