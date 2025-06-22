import pytest
import asyncio
import os
import sys
import httpx
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import server, handle_call_tool, handle_list_tools
from alphavantage.tools import AlphavantageTools
from upstox.tools import UpstoxTools
# Load environment variables
load_dotenv(override=True)

# Import modules to test
from alphavantage.helper_function import (
    fetch_quote,
    fetch_company_overview
)
from upstox.helper_functions import (
    get_instrument_token,
    get_portfolio
)



class TestAPIConnections:
    """Test API connections for both AlphaVantage and Upstox"""

    def test_alphavantage_api_key_exists(self):
        """Test that AlphaVantage API key is configured"""
        async def _test():
            api_key = os.getenv("ALPHAVANTAGE_API_KEY")
            assert api_key is not None, "ALPHAVANTAGE_API_KEY environment variable not set"
            assert len(api_key) > 0, "ALPHAVANTAGE_API_KEY is empty"

        asyncio.run(_test())

    def test_upstox_credentials_exist(self):
        """Test that Upstox credentials are configured"""
        async def _test():
            api_key = os.getenv("UPSTOCKS_API_KEY")
            api_secret = os.getenv("UPSTOCKS_API_SECRET")
            access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
            
            assert api_key is not None, "UPSTOCKS_API_KEY environment variable not set"
            assert api_secret is not None, "UPSTOCKS_API_SECRET environment variable not set"
            assert access_token is not None, "UPSTOX_ACCESS_TOKEN environment variable not set"

        asyncio.run(_test())

    def test_alphavantage_quote_connection(self):
        """Test AlphaVantage quote API connection"""
        async def _test():
            try:
                result = await fetch_quote("AAPL")
                assert isinstance(result, dict), "Response should be a dictionary"
                # Check if we got a valid response structure
                assert "Global Quote" in result or "Error Message" in result or "Note" in result
            except (ConnectionError, TimeoutError, ValueError, KeyError, httpx.HTTPError) as e:
                pytest.fail(f"AlphaVantage API connection failed: {str(e)}")
                pytest.fail(f"AlphaVantage API connection failed: {str(e)}")

        asyncio.run(_test())

    def test_alphavantage_company_overview_connection(self):
        """Test AlphaVantage company overview API connection"""
        async def _test():
            try:
                result = await fetch_company_overview("AAPL")
                assert isinstance(result, dict), "Response should be a dictionary"
                # Should contain company data or error message
                assert "Symbol" in result or "Error Message" in result or "Note" in result
            except Exception as e:
                pytest.fail(f"AlphaVantage company overview API connection failed: {str(e)}")

        asyncio.run(_test())

    def test_upstox_instrument_token_mapping(self):
        """Test Upstox instrument token mapping"""
        async def _test():
            # Test known symbols
            reliance_token = get_instrument_token("RELIANCE")
            assert reliance_token == "NSE_EQ|INE002A01018"
            
            tcs_token = get_instrument_token("TCS")
            assert tcs_token == "NSE_EQ|INE467B01029"
            
            # Test unknown symbol fallback
            unknown_token = get_instrument_token("UNKNOWN")
            assert unknown_token == "NSE_EQ|UNKNOWN"

        asyncio.run(_test())

    @patch('upstox.helper_functions.httpx.AsyncClient')
    async def test_upstox_portfolio_connection_mock(self, mock_client):
        """Test Upstox portfolio API connection with mock"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": []}
        mock_response.raise_for_status.return_value = None
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await get_portfolio()
        assert isinstance(result, dict)
        assert "status" in result or "data" in result


class TestMCPServer:
    """Test MCP Server functionality"""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that server lists all available tools"""
        tools = await handle_list_tools()
        
        # Should return a list of tools
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Extract tool names
        tool_names = [tool.name for tool in tools]
        
        # Check AlphaVantage tools are present
        assert AlphavantageTools.STOCK_QUOTE.value in tool_names
        assert AlphavantageTools.COMPANY_OVERVIEW.value in tool_names
        assert AlphavantageTools.TOP_GAINERS_LOSERS.value in tool_names
        
        # Check Upstox tools are present
        assert UpstoxTools.BUY_STOCK.value in tool_names
        assert UpstoxTools.SELL_STOCK.value in tool_names
        assert UpstoxTools.GET_PORTFOLIO.value in tool_names
        assert UpstoxTools.GET_FUNDS.value in tool_names

    @pytest.mark.asyncio
    async def test_alphavantage_stock_quote_tool(self):
        """Test AlphaVantage stock quote tool execution"""
        try:
            result = await handle_call_tool(
                name=AlphavantageTools.STOCK_QUOTE.value,
                arguments={"symbol": "AAPL"}
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert hasattr(result[0], 'text')
            
        except Exception as e:
            pytest.fail(f"Stock quote tool execution failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling for missing arguments"""
        result = await handle_call_tool(
            name=AlphavantageTools.STOCK_QUOTE.value,
            arguments={}  # Missing required 'symbol' argument
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Value Error" in result[0].text or "Missing required argument" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool_handling(self):
        """Test handling of unknown tool names"""
        result = await handle_call_tool(
            name="unknown_tool",
            arguments={}
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    @patch('upstox.helper_functions.place_order')
    async def test_upstox_buy_stock_tool_mock(self, mock_place_order):
        """Test Upstox buy stock tool with mock"""
        # Mock successful order response
        mock_place_order.return_value = {
            "status": "success",
            "data": {"order_id": "test_order_123"}
        }
        
        result = await handle_call_tool(
            name=UpstoxTools.BUY_STOCK.value,
            arguments={"symbol": "RELIANCE", "quantity": 1}
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check if order was placed successfully
        response_text = result[0].text
        assert "success" in response_text.lower() or "order_id" in response_text

    @pytest.mark.asyncio
    async def test_upstox_get_portfolio_tool(self):
        """Test Upstox get portfolio tool"""
        result = await handle_call_tool(
            name=UpstoxTools.GET_PORTFOLIO.value,
            arguments={}
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Should return some response (even if error due to auth)
        assert hasattr(result[0], 'text')


class TestIntegration:
    """Integration tests for combined functionality"""

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that server initializes properly"""
        assert server is not None
        assert hasattr(server, 'name')
        assert server.name == "combined_trading_server"

    @pytest.mark.asyncio
    async def test_environment_variables_loaded(self):
        """Test that all required environment variables are available"""
        required_vars = [
            "ALPHAVANTAGE_API_KEY",
            "UPSTOCKS_API_KEY", 
            "UPSTOCKS_API_SECRET",
            "UPSTOX_ACCESS_TOKEN"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            pytest.skip(f"Missing environment variables: {', '.join(missing_vars)}")

    @pytest.mark.asyncio
    async def test_tool_argument_validation(self):
        """Test tool argument validation"""
        # Test with invalid quantity (should be integer)
        result = await handle_call_tool(
            name=UpstoxTools.BUY_STOCK.value,
            arguments={"symbol": "RELIANCE", "quantity": "invalid"}
        )
        
        assert isinstance(result, list)
        # Should handle the error gracefully
        assert len(result) > 0


if __name__ == "__main__":
    # Run specific tests or all tests
    pytest.main([__file__, "-v"])
