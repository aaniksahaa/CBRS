import { Box, Heading } from "@chakra-ui/react";
import { useEffect, useState } from "react";

export default function NotFound() {
  return (
    <Box>
      <center>
        <br />
        <br />
        <br />
        <br />
        <br />
        <Heading size="2xl">Error 404!</Heading>
        <br />
        <br />
        <Heading>Sorry, The link you have followed is invalid</Heading>
      </center>
    </Box>
  );
}
